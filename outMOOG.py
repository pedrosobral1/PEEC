# coding=utf-8

import os
import numpy as np
import scipy.io as io
from iron_nlte import iron_nlte
import matplotlib.pyplot as pl

r=io.readsav('/home/pedrosobral/PEEC/NLTE/iron_grid.sav')
rwv=r.get('wv')*10


#FUNCTION outmoog:
#
#	it uses iron_nlte and readoutmoog function to calculate NLTE abundances for some iron lines. These lines are given by an input file (obtained using MOOG method).
#
#
#INPUTS:
#
#	t		Effective temperature [K]
#	g		Logarithm of surface gravity [cgs]
#	fe		Metallicity [Fe/H]
#	x		Microturbulence [km/s]
#	name_input	name of the output MOOG file to read
#	name_output	name of the output txt files
#	rem		removes or keeps the null nlte values
#
#OUTPUTS:
#
#	2 txt files (lte and nlte abundances).
#

def readoutmoog(t,logg,fe,x,name_input,name_output,rem):

	name_ifile="/home/pedrosobral/PEEC/school_codes/running_dir/%s.moog" %name_input

	name_ofile_lte="/home/pedrosobral/PEEC/school_codes/running_dir/results/%s_lte.txt" %name_output

	name_ofile_nlte="/home/pedrosobral/PEEC/school_codes/running_dir/results/%s_nlte.txt" %name_output

	#transform output.moog to txt file
	os.rename(name_ifile, name_ofile_lte)

	om=open(name_ofile_lte,'r')
	
	#creates a new txt file for NLTE abundances
	omnew=open(name_ofile_nlte,'w')
	

	######FE I#####
	
	a=om.read(374) #header
	omnew.write(a)

	for i in range(260): #info about lines
		
		b1=om.read(2)
		b=om.read(8) #wavelenght

		c1=om.read(3)
		c=om.read(8) #ID

		d1=om.read(3)
		d=om.read(5) #EP

		e1=om.read(2)
		e=om.read(6) #loggf

		f1=om.read(4)
		f=om.read(5) #EWin

		g1=om.read(4)
		g=om.read(6) #logRwin

		h1=om.read(4)
		h=om.read(6) #abundance

		i1=om.read(3)
		i=om.read(7) #delavg


		#NLTE calculation

		w=np.where(np.abs(float(b)-rwv)<10**-1)
		
		if tuple(w[0])==():
			nlte=0
			if rem==1:
				continue #continues cycle without printing nlte abundance
			
		else:
			abund=iron_nlte(10.,t,logg,fe,x,w[0][0])
			nlte=abund[1]
			if nlte==-9:
				continue #continues cycle without printing nlte abundance


		#write to the new txt file
		omnew.write(b1),omnew.write(b),omnew.write(c1),omnew.write(c),omnew.write(d1),omnew.write(d),omnew.write(e1),omnew.write(e),omnew.write(f1),omnew.write(f),omnew.write(g1),omnew.write(g),omnew.write(h1),omnew.write(str("%.4f" % nlte)),omnew.write(i1),omnew.write(i)


	#####FE II#####
	f1=om.read(72+80+80+80+1)

	f=om.read(71+76) #header
	omnew.write("\n\n\n\n")
	omnew.write(f)

	for i in range(35): #info about lines
		
		b1=om.read(2)
		b=om.read(8) #wavelenght

		c1=om.read(3)
		c=om.read(8) #ID

		d1=om.read(3)
		d=om.read(5) #EP

		e1=om.read(2)
		e=om.read(6) #loggf

		f1=om.read(4)
		f=om.read(5) #EWin

		g1=om.read(4)
		g=om.read(6) #logRwin

		h1=om.read(4)
		h=om.read(6) #abundance

		i1=om.read(3)
		i=om.read(7) #delavg


		#NLTE calculation

		w=np.where(np.abs(float(b)-rwv)<10**-1)
		
		if tuple(w[0])==():
			nlte=0
			if rem==1:
				continue #continues cycle without printing nlte abundance
		
		else:
			abund=iron_nlte(10.,t,logg,fe,x,w[0][0])
			nlte=abund[1]
			if rem==1:
				continue #continues cycle without printing nlte abundance


		#write to the new txt file
		omnew.write(b1),omnew.write(b),omnew.write(c1),omnew.write(c),omnew.write(d1),omnew.write(d),omnew.write(e1),omnew.write(e),omnew.write(f1),omnew.write(f),omnew.write(g1),omnew.write(g),omnew.write(h1),omnew.write(str("%.4f" % nlte)),omnew.write(i1),omnew.write(i)


	om.close()	
	omnew.close()



def outmoog(t,logg,fe,x,name_input,name_output,rem):
	cmd= "python interpol_MOOG.py %.0f %.0f %.0f %.0f" %(t,logg,fe,x)
	os.system(cmd)
	readoutmoog(t,logg,fe,x,name_input,name_output,rem)

