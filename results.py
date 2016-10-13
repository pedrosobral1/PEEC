# coding=utf-8

from iron_nlte_meu import iron_nlte
import matplotlib.pyplot as pl
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import scipy.io as io
r=io.readsav('/home/pedrosobral/PEEC/NLTE/iron_grid.sav')
rwv=r.get('wv')


# This function prints a .txt doc with difference between LTE and NLTE abundances and a pdf with the respective graphics. Works with 'iron_nlte_meu' function.
#
# We can study this difference's variation with temperature (T), superficial gravity logarithm (g) and metallicity (f), while line index (w), EW (e) and microturbulence (x) are always a fixed value.
#
# We can vary 
#
#INPUTS:
#       t - temperature reference value
#	g - gravity log reference value
#	f - metallicity reference value
#	x - microturbulence reference value (x: x=1 se g>4 ; x=2 se g<4)
#	w - spectral line index
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

	#variables to use in the graphic labels
	tii=ti
	tff=tf
	gii=gi
	gff=gf
	fii=fin
	fff=ff

	###creates .txt with line index name###
	nome= "line %8.3f angs.txt" % (r.get('wv')[w]*10)
	
	res=open(nome,"w")
	res.write("LTE-NLTE abundances difference --> line %8.3f nm \n \n" % (r.get('wv')[w]))
	

	###calculations for variable temperature###
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

	

	###calculations for variable gravity log###
	res.write("\n \nG [%d,%d], dG=%f \n" % (gi,gf,dg))

	#calculate metallity(x) that may change with g values
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



	###calculations for variable metallicity###
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
	

	###graphics###
	res=open(nome,"r")

	#remove -9 entries
	i=tuple(np.where(temp_y!=-9))
	j=tuple(np.where(grav_y!=-9))
	k=tuple(np.where(metal_y!=-9))
	
	temp_y=temp_y[i]
	grav_y=grav_y[j]
	metal_y=metal_y[k]

	temp_x=temp_x[i]
	grav_x=grav_x[j]
	metal_x=metal_x[k]
	
	with PdfPages(("line %8.3f angs_graphs.pdf" % (r.get('wv')[w]*10))) as pdf:

		pl.figure()
		pl.scatter(temp_x,temp_y,color='b',marker='+',s=40)
		pl.title('T [%d,%d] - line %8.3f nm' %(tii,tff,r.get('wv')[w]),color='b')
		pl.xlabel('Temperature [K]',color='b')
		pl.ylabel('LTE-NLTE',color='b')
		pdf.savefig()
		pl.clf()	
		
		pl.figure()	
		pl.scatter(grav_x,grav_y,color='b',marker='+',s=40)
		pl.title('g [%d,%d] - line %8.3f nm' %(gii,gff,r.get('wv')[w]),color='b')
		pl.xlabel('Log surface gravity [cgs]',color='b')
		pl.ylabel('LTE-NLTE',color='b')
		pdf.savefig()
		pl.clf()

		pl.figure()
		pl.scatter(metal_x,metal_y,color='b',marker='+',s=40)
		pl.title('f [%d,%d] - line %8.3f nm' %(fii,fff,r.get('wv')[w]),color='b')
		pl.xlabel('Metallicity [Fe/H]',color='b')
		pl.ylabel('LTE-NLTE',color='b')
		pdf.savefig()
		pl.clf()

	res.close()

