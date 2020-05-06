import os
filename = 'subaru_IB464'
for i in range(10):
    os.chdir(filename+'_OUT/'+filename+f'_{i+1}')
    os.system('cp ' + filename+f'_{i+1}.psf ../../'+filename+'_OUT_John')
    os.system('cp ' + filename+f'_{i+1}.ldac ../../'+filename+'_OUT_John')
    os.chdir('../..')
os.chdir(filename + '_OUT')
os.system('cp '+filename+'_PLOT.pdf ../'+filename+'_OUT_John')
os.chdir('..')
