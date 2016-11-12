# coding=utf-8

import os
import numpy as np
import scipy.io as io
from iron_nlte import iron_nlte
import matplotlib.pyplot as pl
import shutil

r=io.readsav('/home/pedrosobral/PEEC/NLTE/iron_grid.sav')
rwv=r.get('wv')*10


#FUNCTION outmoog:
#
#	it uses iron_nlte and readoutmoog function to calculate NLTE abundances for some iron lines. These lines are given by an input file (obtained using MOOG method).
#
#
#INPUTS:
#
#	dir_input	directory of the MOOG input file (str)
#	name_input	name of the input MOOG file to read (str)
#	dir_output	directory for the output file (str)
#	name_output	name of the output txt files (str)
#	rem		removes (1) or keeps (0) the null nlte values. If 0 is chosen, it calculates the average NLTE abundance for those null points.
#
#OUTPUTS:
#
#	3 txt files (lte, nlte abundances and lines with null nlte values).
#
#CALLING EXAMPLE:
#
#	outmoog("/home/pedrosobral/PEEC","output","/home/pedrosobral/results","mine",1)


def readoutmoog(dir_input,name_input,dir_output,name_output,rem):
		'FUNCTION readoutmoog:\n    it uses iron_nlte function to calculate NLTE abundances for some iron lines. These lines are given by an input file (obtained using MOOG method).\n\nINPUTS:\n    dir_input      directory of the MOOG input file (str)\n    name_input     name of the input MOOG file to read (str)\n    dir_output     directory for the output file (str)\n    name_output    name of the output txt files (str)\n    rem            removes (1) or keeps (0) the null nlte values.If 0 is chosen, it calculates the average NLTE abundance for those null points\n\nOUTPUTS:\n    3 txt files (lte, nlte abundances and lines with null nlte values).\n\nCALLING EXAMPLE:\n    outmoog("/home/pedrosobral/PEEC","output","/home/pedrosobral/results","mine",1)'


	name_ifile="%s/%s.moog" %(dir_input,name_input)

	name_ofile_lte="%s/%s_lte.txt" %(dir_output,name_output)

	if rem==0:
		name_ofile_nlte="%s/%s_nlte.txt" %(dir_output,name_output)
	
	else:
		name_ofile_nlte="%s/%s_nlte_1.txt" %(dir_output,name_output)

	name_ofile_nlte_0="%s/%s_nlte_0.txt" %(dir_output,name_output)

	#copies output.moog to "results" folder
	shutil.copy2(name_ifile,"%s"%dir_output)
	
	#transforms output.moog to txt file
	os.rename("%s/%s.moog" %(dir_output,name_input), name_ofile_lte)

	om=open(name_ofile_lte,'r')
	
	#creates a new txt file for NLTE abundances
	omnew=open(name_ofile_nlte,'w')
	
	#creates a txt file to write lines with null NLTE abundance
	ml=open("%s/%s_null_nlte.txt"%(dir_output,name_output),'w')
	ml.write("Lines with null NLTE abundance \n \n")
	ml.write("FE I \n")
	


	################################### READING AND WRITING FILES ###################################

	size=len(om.readlines())
	
	om=open(name_ofile_lte,'r')

	numbers=['0','1','2','3','4','5','6','7','8','9']

	j=np.array([]) #acumulate for FE I
	l=np.array([]) #acumulate for FE II

	nlte_values_I=np.array([])	
	nlte_values_II=np.array([])
	
	k=0 #count number of iterations
	r=0 #count line number for #lines


	################################### FE I ###################################

	for i in range(size):
		k+=1
		h=om.readline()
			
		if "II" not in h.split(): #while we analyze FE I lines
			

			########analyze .txt line########
	
			if len(h.split()) == 0: #empty txt line
				omnew.write(h)
				continue

	
			if h[2] not in numbers or h[3] not in numbers: #txt line has only information

				if "Teff=" in h.split():
					t=float(h.split()[1])
					logg=float(h.split()[4])
					fe=float(h.split()[8])
					x=float(h.split()[6])
					omnew.write(h)
			
				elif "#lines" in h.split():
					newline=h.replace(h.split()[-1],"%i"%r) 
					av_nlte_I=sum(nlte_values_I)/len(nlte_values_I)
					newline=newline.replace(newline.split()[3],"%.6f"%av_nlte_I)
					#std_nlte_I=np.std(nlte_values_I)
					#newline=newline.replace(newline.split()[6],"%.4f"%std_nlte_I)
					omnew.write(newline)
				else:
					omnew.write(h)



			elif h[2] in numbers or h[3] in numbers: #txt line is an iron line

				r+=1
				wavel=h.split()[0]
				
				###NLTE calculation###
				w=np.where(np.abs(float(wavel)-rwv)<10**-1)
		
				if tuple(w[0])==():
					nlte=0
					j=np.append(j,i)
					ml.write(wavel)
					ml.write("\n")
					if rem==1:
						r-=1
						continue #continues cycle without printing nlte abundance
					else:
						if len(h.split()[6])==7:
							newline=h.replace(h.split()[6]," %.6f"%nlte)
							omnew.write(newline) 
							continue
						else:
							newline=h.replace(h.split()[6],"%.6f"%nlte) 
							omnew.write(newline) 
							continue 

				else:
					abund=iron_nlte(10.,t,logg,fe,x,w[0][0]) 
					nlte=abund[1]
					if nlte==-9:
						j=np.append(j,i)
						ml.write(wavel)
						ml.write("\n")
						if rem==1:
							r-=1
							continue #continues cycle without printing nlte abundance
						else:
							if len(h.split()[6])==7:
								newline=h.replace(h.split()[6]," %.5f"%nlte)
								omnew.write(newline)
								continue 
							else:
								newline=h.replace(h.split()[6],"%.5f"%nlte) 
								omnew.write(newline)
								continue
			
					else:
						nlte_values_I=np.append(nlte_values_I,nlte)
 						if len(h.split()[6])==7:
							newline=h.replace(h.split()[6]," %.6f"%nlte) 
							omnew.write(newline)
							continue
						else:
							newline=h.replace(h.split()[6],"%.6f"%nlte) 
							omnew.write(newline)
							continue 


			else:
				omnew.write(h)

	
		else: 
			break
		


	################################### FE II ###################################

	ml.write("\n\nFE II \n")

	r=0 #count line number for #lines

	for i in range(k,size):

		h=om.readline() 

		#########analyze txt line#########

		if len(h.split()) == 0: #empty txt line
			omnew.write(h)
			continue
	
		if h[2] not in numbers or h[3] not in numbers: #txt line has only information

			if "Teff=" in h.split():
				t=float(h.split()[1])
				logg=float(h.split()[4])
				fe=float(h.split()[8])
				x=float(h.split()[6])
				omnew.write(h)
			
			elif "#lines" in h.split():
				newline=h.replace(h.split()[-1],"%i"%r) 
				av_nlte_II=sum(nlte_values_II)/len(nlte_values_II)
				newline=newline.replace(newline.split()[3],"%.6f"%av_nlte_II)
				#std_nlte_II=np.std(nlte_values_II)
				#newline=newline.replace(newline.split()[6],"%.4f"%std_nlte_II)
				omnew.write(newline)
			else:
				omnew.write(h)


		elif h[2] in numbers or h[3] in numbers: #txt line is an iron line
			
			r+=1
			wavel=h.split()[0]
				
			###NLTE calculation###
			w=np.where(np.abs(float(wavel)-rwv)<10**-1)
		
			if tuple(w[0])==():
				nlte=0
				l=np.append(l,i)
				ml.write(wavel)
				ml.write("\n")
				if rem==1:
					r-=1
					continue #continues cycle without printing nlte abundance
				else:
					if len(h.split()[6])==7:
						newline=h.replace(h.split()[6]," %.6f"%nlte) 
						omnew.write(newline)
						continue
					else:
						newline=h.replace(h.split()[6],"%.6f"%nlte) 
						omnew.write(newline)
						continue 

			else:
				abund=iron_nlte(10.,t,logg,fe,x,w[0][0]) #calculate NLTE abundance
				nlte=abund[1]
				if nlte==-9:
					l=np.append(l,i)
					ml.write(wavel)
					ml.write("\n")
					if rem==1:
						r-=1
						continue #continues cycle without printing nlte abundance
					else:
						if len(h.split()[6])==7:
							newline=h.replace(h.split()[6]," %.5f"%nlte)
							omnew.write(newline)
							continue 
						else:
							newline=h.replace(h.split()[6],"%.5f"%nlte) 
							omnew.write(newline) 
							continue 
					
				else:
					nlte_values_II=np.append(nlte_values_II,nlte)
					if len(h.split()[6])==7:
						newline=h.replace(h.split()[6]," %.6f"%nlte) 
						omnew.write(newline)
						continue
					else:
						newline=h.replace(h.split()[6],"%.6f"%nlte) 
						omnew.write(newline)
						continue 


		else:
			omnew.write(h)

	om.close()	
	omnew.close()
	ml.close()

	


	###change nlte abundance to the average nlte abundance (for the null nlte values lines)###

	if rem==0:

		print av_nlte_I,av_nlte_II
		omnew1=open(name_ofile_nlte,'r')
		size2=len(omnew1.readlines())
		omnew1=open(name_ofile_nlte,'r')
	
		omnew2=open(name_ofile_nlte_0,'w') 

		#insert average value	
		for i in range(size2):
			h=omnew1.readline() #readline 

			if i in j:
				newline=h.replace(newline.split()[6],"%.6f"%av_nlte_I)
				omnew2.write(newline) #write the line with average nlte abundance

			elif i in l:
				newline=h.replace(newline.split()[6],"%.6f"%av_nlte_II)
				omnew2.write(newline) #write the line with average nlte abundance

			else:
				omnew2.write(h)	

	
		omnew2.close()
		os.remove(name_ofile_nlte)
