# coding=utf-8

from mpl_toolkits.mplot3d import Axes3D
from iron_nlte_meu_3d import iron_nlte_3d
import matplotlib.pyplot as pl
import matplotlib.cm as cm
from matplotlib.collections import PolyCollection
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import scipy.io as io
from scipy import ndimage
r=io.readsav('/home/pedrosobral/PEEC/NLTE/iron_grid.sav')
rwv=r.get('wv')


# This function prints a pdf with 3D graphics with LTE-NLTE abundances differences. Works with 'iron_nlte_meu_3d'.
#
# We can study it this way:
#	1- temperature (t) and surface gravity logarithm (g) graph;
#	2- surface gravity logarithm (g) and metallicity (f) graph;
#	3- temperature (t) and metallicity (f) graph.
# 
#	while line index (w), EW (e) and microturbulence (x) are a fixed value.
#
#
# HOW TO USE: we can only choose one of the above and to do that, we put the variable increment (the variable we want to fix) with the 0 value.
#
# EXAMPLE: result_3d(2,2420,4000,8000,250,1.0,5.0,0.7,-0.2,0.5,0)
#
#
#
#INPUTS:
#	(x: x=1 se g>4 ; x=2 se g<4)
#	w - spectral line index
#	
#	ti - initial temperature
#	tf - final temperature
#	dt - temperature increment
#
#	gi - initial surface gravity logarithm
#	gf - final surface gravity logarithm
#	dg - surface gravity logarithm increment
#
#	fin - initial metallicity
#	ff - final metallicity
#	df - metallicity increment


def result_3d(w,ti,tf,dt,gi,gf,dg,fin,ff,df):
	
	###fixed metallicity###
	if df==0:
		t=np.arange(ti,tf+1e-8,dt)
		g=np.arange(gi,gf+1e-8,dg)
		f=fin
		horiz=g.size
		X,Y=np.meshgrid(t,g)
		Xlabel='Temperature [K]'
		Ylabel='Log surface gravity [cgs]'
		fig_name='line %8.3f angs' %(rwv[w]*10)
		n='Temp-Grav variation'

	###fixed surface gravity logarithm###
	elif dg==0:
		t=np.arange(ti,tf+1e-8,dt)
		g=gi
		f=np.arange(fin,ff+1e-8,df)
		horiz=f.size
		X,Y=np.meshgrid(t,f)
		Xlabel='Temperature [K]'
		Ylabel='Metallicity [Fe/H]'
		fig_name='line %8.3f angs' %(rwv[w]*10)
		n='Grav-Metal variation'

	###fixed temperature##
	elif dt==0:
		t=ti
		g=np.arange(gi,gf+1e-8,dg)
		f=np.arange(fin,ff+1e-8,df)
		horiz=f.size
		X,Y=np.meshgrid(g,f)
		Xlabel='Log surface gravity [cgs]'
		Ylabel='Metallicity [Fe/H]'
		fig_name='line %8.3f angs' %(rwv[w]*10)
		n='Temp-Metal variation'


	###Z label###
	Zlabel='LTE-NLTE'


	###calculate LTE-NLTE abundance differences###
	abund=iron_nlte_3d(10,t,g,f,w)	


	###remove -9 entries and change it to nan###
	for i in range(horiz):
		i0=np.where(abund[i]==-9)
		X[i][i0[0]]=np.nan
		Y[i][i0[0]]=np.nan
		abund[i][i0[0]]=np.nan


	###graphics###
	with PdfPages(("line %8.3f angs, %s.pdf" % (r.get('wv')[w]*10,n))) as pdf:

		fig = pl.figure()
		fig.set_size_inches(12,7)
		ax = fig.gca(projection='3d')
		ax.scatter(X,Y,abund,c='r')
		ax.set_xlabel(Xlabel,color='r')
		ax.set_ylabel(Ylabel,color='r')
		ax.set_zlabel(Zlabel,color='r')
		ax.view_init(elev=18,azim=-147)	
		pdf.savefig()	
		pl.clf()

