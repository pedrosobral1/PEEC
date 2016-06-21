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


#Função result_3d imprime um pdf com gráfico 3D da diferença entre abundancias LTE e NLTE. Trabalha com a função iron_nlte_meu_3d.
#
#
#
# Podemos estudar como varia esta diferenca com: 
#	1- temperatura (t) e logaritmo da gravidade superficial (g);
#	2- logaritmo da gravidade superficial (g) e metalicidade (f);
#	3- temperatura (t) e metalicidade (f). 
#enquanto índice de linha (w), largura equivalente (e) e microturbulencia (x) sao 1 valor fixo dado.
#
#
#
# COMO USAR: apenas podemos escolher uma das hipóteses acima e, para isso, coloca-se o incremento da variável (temp, grav superf ou metalic) que queremos fixar, com o valor 0.
#
# EXEMPLO: result_3d(2,2420,4000,8000,250,1.0,5.0,0.7,-0.2,0.5,0)
#
#
#
#INPUTS:
#	x - valor referencia microturbulencia
#	w - indice da risca espectral
#	
#	ti - temperatura inicial
#	tf - temperatura final
#	dt - incremento entre temperaturas
#
#	gi - log gravidade inicial
#	gf - log gravidade final
#	dg - incremento entre log gravidade
#
#	fin - metalicidade inicial
#	ff - metalicidade final
#	df - incremento entre metalicidades


def result_3d(x,w,ti,tf,dt,gi,gf,dg,fin,ff,df):
	
	###caso metalicidade seja fixada###
	if df==0:
		t=np.arange(ti,tf+1e-8,dt)
		g=np.arange(gi,gf+1e-8,dg)
		f=fin
		horiz=g.size
		X,Y=np.meshgrid(t,g)
		Xlabel='Temperature [K]'
		Ylabel='Log surface gravity [cgs]'
		fig_name='risca %8.3f angs' %(rwv[w]*10)
		n='Temp-Grav variation'

	###caso grav superf seja fixada###
	elif dg==0:
		t=np.arange(ti,tf+1e-8,dt)
		g=gi
		f=np.arange(fin,ff+1e-8,df)
		horiz=f.size
		X,Y=np.meshgrid(t,f)
		Xlabel='Temperature [K]'
		Ylabel='Metallicity [Fe/H]'
		fig_name='risca %8.3f angs' %(rwv[w]*10)
		n='Grav-Metal variation'

	###caso temperatura seja fixada##
	elif dt==0:
		t=ti
		g=np.arange(gi,gf+1e-8,dg)
		f=np.arange(fin,ff+1e-8,df)
		horiz=f.size
		X,Y=np.meshgrid(g,f)
		Xlabel='Log surface gravity [cgs]'
		Ylabel='Metallicity [Fe/H]'
		fig_name='risca %8.3f angs' %(rwv[w]*10)
		n='Temp-Metal variation'


	###legenda Z###
	Zlabel='LTE-NLTE'


	###calculo da diferença das abundancias LTE e NLTE###
	abund=iron_nlte_3d(10,t,g,f,x,w)	


	###retirar entradas -9 e transformar em nan###
	for i in range(horiz):
		i0=np.where(abund[i]==-9)
		X[i][i0[0]]=np.nan
		Y[i][i0[0]]=np.nan
		abund[i][i0[0]]=np.nan


	###gráficos###
	with PdfPages(("risca %8.3f angs, microturbulence %1.1f %s.pdf" % (r.get('wv')[w]*10,x,n))) as pdf:

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
