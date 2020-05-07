import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits

filename = 'subaru_IB464.ldac'
x = 'FLUX_RADIUS'
y = 'MAG_APER'
table = fits.open('../../../../media/sf_COSMOS2020/'+filename,
                  ignore_missing_end=True, mode='update')

tab_ldac = table['LDAC_OBJECTS'].data
# report to user
n_obj = len(tab_ldac)
xlims, ylims = (3.3, 5.4), (18.7, 22.0)
mask_ldac = (tab_ldac[y] > ylims[0]) &\
    (tab_ldac[y] < ylims[1]) &\
    (tab_ldac[x] > xlims[0]) &\
    (tab_ldac[x] < xlims[1])
print(max(tab_ldac[x]), min(tab_ldac[x]))
print(max(tab_ldac[y]), min(tab_ldac[y]))
# print(tab_ldac.names, n_obj)
fig, ax = plt.subplots(figsize=(12, 9))
ax.plot(tab_ldac[x], tab_ldac[y],
        'bo', alpha=0.3, markersize=2, label='All objects')
ax.plot(tab_ldac[x][mask_ldac], tab_ldac[y]
        [mask_ldac], 'ro', alpha=0.2, label='Selected objects')
ax.set(title='Selected {}/{} objects in {},{}-box'.format(sum(mask_ldac), n_obj, str(xlims), str(ylims)),
       xlim=(0,  15*2), ylim=(0, 30), xlabel=x, ylabel=y)
plt.gca().invert_yaxis()
plt.legend()
# fig.savefig('selection_'+filename[:12]+'.png')
fig.show()

table['LDAC_OBJECTS'].data = tab_ldac[mask_ldac]
table.writeto(filename[:12]+'_clean'+'.ldac', overwrite=1)
