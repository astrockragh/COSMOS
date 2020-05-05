import os
band = 'subaru_IB464'
names = []
cats = []
for i in range(10):
    names.append(band+'_{}'.format(i+1))
    cats.append(band+'_{}.ldac'.format(i+1))
print(cats)
for j in range(10):
    os.chdir(f'subaru_IB464_OUT/{names[j]}')
    command = f'psfex {cats[j]} -c ../../config_constant.psfex'
    os.system(command)
    os.chdir(f'../..')
