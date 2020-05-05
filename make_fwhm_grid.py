import numpy as np 
import matplotlib.pyplot as plt 
from astropy.io import fits
from astropy.table import Table
from scipy import stats
import os
from astropy import wcs
import sys

# MUST DO FIRST:
# 1. Select candidate pointsources + produce plot
# 2. THEN RUN THIS CODE
# 3. Generate sub-catalogs with sources within each FWHM_IMAGE bin
# 4. Run PSFEx over each sub-catalog with EXACT SAME FILENAME AS INPUT HERE


# User Input
FILENAME = sys.argv[1] #'subaru_IB464_clean.ldac'   # must already be CLEAN!
FILE_ID_PREFIX = FILENAME.split('_clean')[0] #'subaru_IA464'
TABLE_OUTPUT_NAME = FILE_ID_PREFIX+'_GRIDPT.dat'
WORKING_DIR = '.'
OUTPUT_DIR = FILE_ID_PREFIX + '_OUT'
TABLE_OUTPUT_PATH = os.path.join(OUTPUT_DIR, TABLE_OUTPUT_NAME)
OVERWRITE = True
MOSAIC_SIZE = (48096, 48096)
DBINS = (2004, 2004)        # SPATIAL GRID
DYN_RANGE = (-0.15, 0.15)  # PLOTTING ONLY
FWHM_RANGE = (-0.2, 0.2)  # coarse cut to remove extreme outliers
PSF_NSNAP = 10              # number of PSF snapshots to make -- FWHM GRID
PLOT = 1
MAKE_SUBCATALOGS = True
plt.ioff()


# Open the file
fname = os.path.join(WORKING_DIR, FILENAME)
print(f'Trying to open {fname}')
hdul = fits.open(fname, ignore_missing_end=True)
print(hdul.info())
catalog = Table(hdul['LDAC_OBJECTS'].data)
fwhm_image = catalog['FWHM_IMAGE']

if not os.path.exists(OUTPUT_DIR):
    print(f'Creating output directory: {OUTPUT_DIR}')
    os.system(f'mkdir {OUTPUT_DIR}')

# Create grid
xedges, yedges = np.arange(0, MOSAIC_SIZE[0], DBINS[0]), np.arange(0, MOSAIC_SIZE[1], DBINS[1])
print(f'Creating {len(xedges)}x{len(yedges)} grid')
med_fwhm = np.median(catalog['FWHM_IMAGE'])
Hstd, xedges, yedges, loc = stats.binned_statistic_2d(catalog['X_IMAGE'], catalog['Y_IMAGE'], 
                                               values=fwhm_image, statistic='std', bins=(xedges, yedges))
H, xedges, yedges, loc = stats.binned_statistic_2d(catalog['X_IMAGE'], catalog['Y_IMAGE'], 
                                               values=fwhm_image, statistic='median', bins=(xedges, yedges))
bin_id, counts = np.unique(loc, return_counts=True)
print(f'Pre-digitize: Average of {np.mean(counts):3.3f} sources in a spatial bin.')

# Compute grid points
xcenters, ycenters = xedges[:-1] + DBINS[0]/2., yedges[:-1] + DBINS[1]/2.
mx, my = np.meshgrid(xcenters, ycenters)
mmx, mmy = mx[~np.isnan(H.T)], my[~np.isnan(H.T)]

# Make FWHM grid
def histedges_equalN(x, nbin):
    npt = len(x)
    return np.interp(np.linspace(0, npt, nbin + 1),
                     np.arange(npt),
                     np.sort(x))

narrow_fwhm_image = fwhm_image[(fwhm_image - med_fwhm > FWHM_RANGE[0]) & (fwhm_image - med_fwhm < FWHM_RANGE[1])]
bin_edges = histedges_equalN(narrow_fwhm_image, PSF_NSNAP)
fwhm_grid = bin_edges[:-1] + np.ediff1d(bin_edges)/2.
plt.close('all')


# Assign gridpoints to nearest FWHM gridpoint
digit_H = -99 * np.ones_like(H)
k=-1
digit_loc = []
for i in np.arange(H.shape[0]):
    for j in np.arange(H.shape[1]):
        k+=1
        if np.isnan(H[i,j]):
            continue
        diff = abs(H[i,j] - fwhm_grid)
        mindiff = np.min(diff)
        grid_val = fwhm_grid[diff == mindiff][0]
        digit_H[i,j] = grid_val
        print(f'{k} :: {grid_val:2.2f}  ({H[i,j] + med_fwhm:2.2f}, {mindiff:2.2f})')
        digit_loc.append(k)

# assert(len(np.unique(digit_H)) - 1 == PSF_NSNAP)
digit_H[digit_H<0] = np.nan

digit_bin_id, digit_counts = np.unique(digit_H, return_counts=True)
print(f'Post-digitize: Average of {len(narrow_fwhm_image)/PSF_NSNAP:2.2f} sources in each of {len(fwhm_grid)} FWHM bins')
eacc = np.std(H.T[~np.isnan(H.T)] - digit_H.T[~np.isnan(H.T)])
print(f'Expected FWHM accuracy: {eacc:3.3f} px')

# Create a new WCS object.  The number of axes must be set
# from the start
w = wcs.WCS(naxis=2)

# Set up an "Airy's zenithal" projection
# Vector properties may be set with Python lists, or Numpy arrays
w.wcs.crpix = [2.271550000000E+04, 2.184100000000E+04]
w.wcs.cdelt = np.array([-4.166666800000E-05, 4.166666800000E-05])
w.wcs.crval = [1.501163213000E+02, 2.200973097000E+00]
w.wcs.ctype = ["RA---AIR", "DEC--AIR"]

ra, dec = w.wcs_pix2world(mmx, mmy, 1)


# Write output

# RA, DEC, X, Y, ID_GRIDPT, MEDIAN_FWHM, GRID_FWHM, FILE_ID
FileID = []
for i in digit_H.T[~np.isnan(H.T)]:
    FileID.append(f'{FILE_ID_PREFIX}_{np.argwhere(fwhm_grid==i)[0][0] + 1}')

tab =  Table([ra, dec, mmx, mmy, digit_loc, H.T[~np.isnan(H.T)], digit_H.T[~np.isnan(H.T)], FileID], names=['RA', 'Dec', 'X_IMAGE', 'Y_IMAGE', 'ID_GRIDPT', 'MEDIAN_FWHM', 'GRID_FWHM', 'FILE_ID'])
print(f'Writing out grid table to {TABLE_OUTPUT_NAME}')
tab.write(TABLE_OUTPUT_PATH, overwrite=OVERWRITE, format='ascii.tab')

data = hdul['LDAC_OBJECTS'].data.copy()
for i, fwhm in enumerate(fwhm_grid):
    binlo, binhi = bin_edges[i:i+2]
    hdul['LDAC_OBJECTS'].data = data[(catalog['FWHM_IMAGE']>binlo) & (catalog['FWHM_IMAGE']<binhi)]
    outfilename = f'{FILE_ID_PREFIX}_{i+1}.ldac'
    print(f'Writing out sub-catalog for #{i+1} ({fwhm:3.3f}px) to {outfilename}')
    outpath = os.path.join(OUTPUT_DIR, outfilename)
    hdul.writeto(outpath, overwrite=OVERWRITE)


if PLOT > 0:
    fig, ax = plt.subplots(ncols=4, figsize=(25, 7), gridspec_kw={'width_ratios': [1, 1, 1, 2]} )
    h = ax[0].imshow(H.T - med_fwhm, cmap='coolwarm', vmin=DYN_RANGE[0], vmax=DYN_RANGE[1], extent=(0, xedges[-1], 0, yedges[-1]))
    ax[0].scatter(mmx, mmy, marker='x', c='k', alpha=0.5)
    plt.colorbar(h, ax=ax[0], orientation="horizontal")
    h = ax[1].imshow(Hstd.T, cmap='Greens', extent=(0, xedges[-1], 0, yedges[-1]))
    plt.colorbar(h, ax=ax[1], orientation="horizontal")
    # ax[1].scatter(mmx, mmy, marker='x', c='k', alpha=0.5)
    
    ax[2].imshow(digit_H.T - med_fwhm, cmap='coolwarm', vmin=DYN_RANGE[0], vmax=DYN_RANGE[1], extent=(0, xedges[-1], 0, yedges[-1]))
    
    ax[2].text(0.01, 1.01, s=f'{FILENAME}', transform=ax[0].transAxes)


    ax[3].hist(fwhm_image, bins=np.arange(med_fwhm+DYN_RANGE[0], med_fwhm+DYN_RANGE[1]+0.01, 0.01), histtype='step', label='Input sources')
    [ax[3].axvline(i, ls='dashed', c='grey', alpha=0.8) for i in bin_edges]
    # [x[2].axvline(i, ls='solid', c='grey') for i in fwhm_grid]
    ax[3].hist(H[~np.isnan(H)].flatten(), bins=np.arange(med_fwhm+DYN_RANGE[0], med_fwhm+DYN_RANGE[1]+0.01, 0.01), histtype='step', label='Spatial bins')
    ax[3].hist(digit_H[~np.isnan(H)].flatten(), histtype='step', bins=bin_edges, label='Digitized spatial bins')
    ax[2].text(0.01, 1.01, s=f'N={len(fwhm_image)} | Median(FWHM) = {med_fwhm:3.3f} px', transform=ax[2].transAxes)
    ax[3].set_xlim(med_fwhm+DYN_RANGE[0], med_fwhm+DYN_RANGE[1])
    
    ax[3].axvline(med_fwhm, ls='dotted', c='grey')
    ax[3].set_xlabel('FWHM_IMAGE')
    ax[3].legend()

    fig.savefig(os.path.join(OUTPUT_DIR, f'{FILE_ID_PREFIX}_PLOT.pdf'))