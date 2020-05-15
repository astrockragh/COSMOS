import os
import ast
with open('limits.txt', 'r') as file:
    limits = ast.literal_eval(file.read())
band = list(limits.keys())[13]
name = 'subaru_'+band
names = []
cats = []
for i in range(10):
    names.append(band+'_{}'.format(i+1))
    cats.append(name+'_{}.ldac'.format(i+1))
for j in range(10):
    os.chdir(name+'_OUT')
    command = f'psfex {cats[j]} -c ../config_constant.psfex'
    os.system(command)
    os.chdir(f'..')
filename = 'subaru_'+band
os.chdir(filename + '_OUT')
os.system('mkdir '+filename+'_John')
for i in range(10):
    os.system('mv ' + filename+f'_{i+1}.psf ' + filename+'_John')
    os.system('mv ' + filename+f'_{i+1}.ldac '+filename+'_John')
os.system('mv '+filename+'_PLOT.pdf '+filename+'_John')
os.system('mv '+filename+'_GRIDPT.dat '+filename+'_John')
os.chdir('..')
os.system('cp '+filename+'_selection.png '+filename+'_OUT/'+filename+'_John')
