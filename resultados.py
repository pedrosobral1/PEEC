# coding=utf-8

from iron_nlte_meu import iron_nlte
import matplotlib.pyplot as pl
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import scipy.io as io
r=io.readsav('/home/pedrosobral/PEEC/NLTE/iron_grid.sav')
rwv=r.get('wv')


#Função result imprime um doc .txt com a diferença entre abundancias LTE e NLTE, indicando quais as variaveis fixas em cada momento.
#
# Podemos estudar como varia esta diferenca com a temperatura (t), logaritmo da gravidade superficial (g), metalicidade (f) e índice de linha (w), enquanto largura equivalente (e) e microturbulencia (x) sao sempre fixas.
#
#INPUTS:
#       t - valor referencia temperatura 
#	g - valor referencia log gravidade 
#	f - valor referencia metalicidade
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


def result(t,g,f,x,w,ti,tf,dt,gi,gf,dg,fin,ff,df):

	###criar ficheiro .txt com dado nome###
	nome= "risca %8.3f angs.txt" % (r.get('wv')[w]*10)
	
	res=open(nome,"w")
	res.write("ABUNDANCIA LTE vs NLTE --> risca %8.3f nm \n \n" % (r.get('wv')[w]))
	

	###calculos para temperatura variavel###
	temp_x=np.array([ti])
	res.write("T [%d,%d], dT=%f \n" % (ti,tf,dt))
	temp=temp=iron_nlte(10.,ti,g,f,x,w)
	temp_y=np.array([temp[2]])
	res.write( "%f \n" % (temp[2]))
	for te in range(ti+dt,tf+dt,dt):
		temp=iron_nlte(10.,te,g,f,x,w)
		temp_x=np.append(temp_x,te)
		temp_y=np.append(temp_y,temp[2])
		res.write( "%f \n" % (temp[2]))

	

	###calculos para log grav variavel###
	res.write("\n \nG [%d,%d], dG=%f \n" % (gi,gf,dg))

	#calcular metalicidade (x) que poderá mudar c/ valor de g
	if gi<4:
		xg=2
	else:
		xg=1
	grav_x=np.array([gi])
	grav=iron_nlte(10.,t,gi,f,xg,w)
	grav_y=np.array([grav[2]])	
	res.write( "%f \n" % (grav[2]))
	for i in range(int((gf-gi)/dg)):
		gi+=dg
		grav=iron_nlte(10.,t,gi,f,xg,w)
		grav_x=np.append(grav_x,[gi])
		grav_y=np.append(grav_y,grav[2])	
		res.write( "%f \n" % (grav[2]))



	###calculos para metalicidade variavel###
	metal_x=np.array([fin])
	res.write("\n \nF [%d,%d], dF=%f \n" % (fin,ff,df))
	metal=iron_nlte(10.,t,g,fin,x,w)
	metal_y=np.array([metal[2]])	
	res.write( "%f \n" % (metal[2]))
	for j in range(int((ff-fin)/df)):
		fin+=df
		metal=iron_nlte(10.,t,g,fin,x,w)	
		metal_x=np.append(metal_x,[fin])
		metal_y=np.append(metal_y,metal[2])			
		res.write( "%f \n" % (metal[2]))	

	res.close()
	

	###gráficos###
	res=open(nome,"r")

	#remover entradas -9
	i=tuple(np.where(temp_y!=-9))
	j=tuple(np.where(grav_y!=-9))
	k=tuple(np.where(metal_y!=-9))
	
	temp_y=temp_y[i]
	grav_y=grav_y[j]
	metal_y=metal_y[k]

	temp_x=temp_x[i]
	grav_x=grav_x[j]
	metal_x=metal_x[k]
	
	with PdfPages(("risca %8.3f angs_graphs.pdf" % (r.get('wv')[w]*10))) as pdf:

		pl.figure()
		pl.scatter(temp_x,temp_y,color='r',marker='+')
		pl.title('LTE vs NLte c/ Temp')
		pdf.savefig()
		pl.clf()	
		
		pl.figure()	
		pl.scatter(grav_x,grav_y,color='r',marker='+')
		pl.title('LTE vs NLTE c/ Surf Grav')
		pdf.savefig()
		pl.clf()

		pl.figure()
		pl.scatter(metal_x,metal_y,color='r',marker='+')
		pl.title('LTE vs NLTE c/ Metal')
		pdf.savefig()
		pl.clf()

	res.close()






