# coding=utf-8

#histograma com correcçoes das riscas todas/ sol, estr quente (6400K), estr fria (4500K),estr fria (4500K ,logg=2)/ outros 4 com metal=-1

#parametros sol
#	t=5777K
#	logg=4.44
#	fe=0.02
#	microturb=1.02



import os
import numpy as np
import scipy.io as io
import sys
from iron_nlte import iron_nlte
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as pl

r=io.readsav('/home/pedrosobral/PEEC/NLTE/iron_grid.sav')
rwv=r.get('wv')*10


def nlte_correction_grid(t,logg,fe,x,rem):
	
	'FUNCTION nlte_correction:\n    creates an histogram with the NLTE/LTE abundances difference for all the iron lines\n\nINPUTS:\n    t        temperature\n    logg     surface gravity logarithm\n    fe       metallicity\n    x        microturbulence\n    rem      removes all the null points (1), or not (0)\n\n'

	nlte_corr=np.array([])

	for i in range(len(rwv)):

		nlte=iron_nlte(10.,t,logg,fe,x,i)

		nlte_corr=np.append(nlte_corr,nlte[2])

	if rem==1:
		w=np.where(nlte_corr!=-9)
		nlte_corr_new=nlte_corr[w]
		nlte_corr=nlte_corr_new
	


	with PdfPages(("%4.0f, %2.2f, %1.2f, %1.2f | temp,logg,fe,x.pdf" % (t,logg,fe,x))) as pdf:

		pl.figure()
		pl.hist(nlte_corr,bins=50)
		pl.title("temp= %4.0f, logg= %2.3f, fe= %1.2f, x= %1.2f" % (t,logg,fe,x))
		pl.xlabel('LTE-NLTE',color='b')
		pdf.savefig()
		pl.clf()


#if __name__ == '__main__':
  
	#nlte_correction(float(sys.argv[1]),float(sys.argv[2]),float(sys.argv[3]),float(sys.argv[4]),float(sys.argv[5]))
