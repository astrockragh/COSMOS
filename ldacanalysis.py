import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits

filename = 'subaru_IA484.ldac'

table = fits.open(filename,
                  ignore_missing_end=True, mode='update')

tab_ldac = table['LDAC_OBJECTS'].data
# report to user
n_obj = len(tab_ldac)
xlims, ylims = (5, 6.7), (15, 21)
mask_ldac = (tab_ldac['MAG_APER'] > ylims[0]) &\
    (tab_ldac['MAG_APER'] < ylims[1]) &\
    (tab_ldac['FWHM_IMAGE'] > xlims[0]) &\
    (tab_ldac['FWHM_IMAGE'] < xlims[1])

# print(tab_ldac.names, n_obj)
fig, ax = plt.subplots(figsize=(12, 9))
ax.plot(tab_ldac['FWHM_IMAGE'], tab_ldac['MAG_APER'],
        'bo', label='All objects')
ax.plot(tab_ldac['FWHM_IMAGE'][mask_ldac], tab_ldac['MAG_APER']
        [mask_ldac], 'ro', label='Selected objects')
ax.set(xlim=(5, 7), ylim=(15, 25), xlabel='FWHM', ylabel='MAG_APER')
plt.gca().invert_yaxis()
plt.legend()
fig.show()


table['LDAC_OBJECTS'].data = tab_ldac[mask_ldac]
table.writeto(filename[:12]+'_clean'+'.ldac', overwrite=1)
