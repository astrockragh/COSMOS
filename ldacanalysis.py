import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import ast
with open('limits.txt', 'r') as file:
    limits = ast.literal_eval(file.read())
# remember to check index
band = list(limits.keys())[13]
x = 'FWHM_IMAGE'
y = 'MAG_APER'
table = fits.open('../../../../media/sf_COSMOS2020/'+'subaru_'+band+'.ldac',
                  ignore_missing_end=True, mode='update')
firsttry = 0
tab_ldac = table['LDAC_OBJECTS'].data
# report to user
n_obj = len(tab_ldac)
if firsttry == 1:
    xlims, ylims = (0, 0), (0, 0)
else:
    xlims, ylims = limits[band]
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
        [mask_ldac], 'ro', alpha=0.05, label='Selected objects')
if firsttry == 1:
    ax.set(title='Selected {}/{} objects in {},{}-box from {}'.format(sum(mask_ldac), n_obj, str(xlims), str(ylims), band),
           xlim=(0,  15*2), ylim=(0, 30), xlabel=x, ylabel=y)
else:
    ax.set(title='Selected {}/{} objects in {},{}-box from {}'.format(sum(mask_ldac), n_obj, str(xlims), str(ylims), band),
           xlim=(xlims[0]-2,  xlims[1]+3), ylim=(ylims[0]-2,  ylims[1]+3), xlabel=x, ylabel=y)
plt.gca().invert_yaxis()
plt.legend()
if firsttry == 0:
    fig.savefig('subaru_'+band+'_selection.png')
fig.show()

table['LDAC_OBJECTS'].data = tab_ldac[mask_ldac]
table.writeto('subaru_'+band+'_clean.ldac', overwrite=1)
