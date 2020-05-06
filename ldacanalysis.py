import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits

filename = 'subaru_IB464.ldac'

table = fits.open(filename,
                  ignore_missing_end=True, mode='update')

tab_ldac = table['LDAC_OBJECTS'].data
# report to user
n_obj = len(tab_ldac)
xlims, ylims = (5.6, 6.3), (17.7, 20.3)
mask_ldac = (tab_ldac['MAG_APER'] > ylims[0]) &\
    (tab_ldac['MAG_APER'] < ylims[1]) &\
    (tab_ldac['FWHM_IMAGE'] > xlims[0]) &\
    (tab_ldac['FWHM_IMAGE'] < xlims[1])

# print(tab_ldac.names, n_obj)
fig, ax = plt.subplots(figsize=(12, 9))
ax.plot(tab_ldac['FWHM_IMAGE'], tab_ldac['MAG_APER'],
        'bo', alpha=0.3, markersize=2, label='All objects')
ax.plot(tab_ldac['FWHM_IMAGE'][mask_ldac], tab_ldac['MAG_APER']
        [mask_ldac], 'ro', alpha=0.05, label='Selected objects')
ax.set(title='Selected {}/{} objects'.format(sum(mask_ldac), n_obj),
       xlim=(5,  7), ylim=(15, 25), xlabel='FWHM', ylabel='MAG_APER')
plt.gca().invert_yaxis()
plt.legend()
fig.savefig('selection_'+filename[:12]+'.png')
fig.show()

table['LDAC_OBJECTS'].data = tab_ldac[mask_ldac]
table.writeto(filename[:12]+'_clean'+'.ldac', overwrite=1)
