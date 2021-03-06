
# coding=utf-8
import numpy as np
import inspect as ip
import scipy.io as io
import time
import sys
import os
import ast

######common variables######
r=io.readsav('/home/pedrosobral/PEEC/NLTE/iron_grid.sav')
#r=ast.literal_eval(os.environ["IRON_GRID"])
rwl=r.get('wl')
rwn=r.get('wn')
rfg=r.get('fg')
rtg=r.get('tg')
rgg=r.get('gg')
rxg=r.get('xg')	
rwv=r.get('wv')
rgf=r.get('gf')
rel=r.get('el')
rio=r.get('io')


##########################################################################


def find_index(y,x): #y,x are arrays
	ii=np.where(np.absolute(y-x) < 1e-8) #tuple (array([index]),)
	i=tuple(ii[0]) #tuple that satisfies the condition

	if i != (): #if there are index satifying the cond
		i=np.array([i[0],i[0]])
	else:
		uu=np.where(y>x)
		u=tuple(uu[0])
		ll=np.where(y<x)
		l=tuple(ll[0])
		if u != (): 
			u=u[0]
		if l != (): 
			l=l[len(l)-1]
		if u == () or l  == ():
			i=()
		else:
			i=[l,u]
			i=np.sort(i) #arrange ind

	return i

t0=time.clock()
##########################################################################

#FUNCTION iron_nlte:
#
#	it allows the calculation of LTE/NLTE abundances for a given neutral iron EW, using linear interpolation
#
#
#INPUTS: 
#
#       e          [0.1,500]       Equivalent width [pm] (optional)
#       t          [4000.0,8000.0] Effective temperature [K]
#       g          [1.0,5.0]       Logarithm of surface gravity [cgs] 
#       f          [-5.0,0.5]      Metallicity [Fe/H]
#       x          [1,5]           Microturbulence [km/s]      
#       w          [0,3345]        Line index
#     
#       al         [0,1]           Flag for LTE abundance. If al=1, "e" is treated as an output. If al=0, f is ignored.
#
#
#OUTPUTS:
#
#	LTE, NLTE abundances and its difference.
#

al=1
silent=True #False = prints everything

def iron_nlte(e,t,g,f,x,w,al=al,silent=silent):
	
	#####verify input parameters#####
	#if len(tuple(ip.getargspec(iron_nlte)[0])) != 8:
		#print ('CALLING SEQUENCE:\n	a=iron_nlte(e,t,g,f,x,w,/al) \nINPUTS: \n       e          [0.1,500]       Equivalent width [pm] (optional)\n       t          [4000.0,8000.0] Effective temperature [K])\n       g          [1.0,5.0]       Logarithm of surface gravity [cgs]\n       f          [-5.0,0.5]      Metallicity [Fe/H] (LTE)\n       x          [1,5]           Microturbulence [km/s]\n       w          [0,3345]        Line index\n\n       al         [0,1]           If flag is set, f is fixed and e\n                                  returned (optional)\n')                                                 
		#return [-9,-9,-9]
	
	t1=time.clock()

	mg,f=rfg+7.45,f+7.45

	#####finds temp, surf grav and microturb indices#####
	ti=find_index(rtg,t)
	gi=find_index(rgg,g)
	xi=find_index(rxg,x)
	li=w
	
	######line info#######
	if not silent:
		print ('Using calculations for %8.3f nm, EV_low= %7.3f eV, log(gf)= %7.3f' % (r.get('wv')[li],r.get('el')[li],np.log10(r.get('gf')[li])))

	######verifies if parameters are in the allowed range######
		#equiv width	
	if not silent:
		if e < 0.1 or e > 100:
			if not silent:
				print ('Equivalent width outside range')
			return [-9,-9,-9]
	
		#eff temp
	if ti == ():
		if not silent:
			print ('Effective temperature outside range')
		return np.array([-9,-9,-9])

		#line index
	if li < 0 or li > 3345:
		if not silent:
			print ('Line index outside range')
		return np.array([-9,-9,-9])

		#surf gravity
	if gi == ():
		if not silent:
			print ('Surface gravity outside range')
		return np.array([-9,-9,-9])

		#microturb
	if xi == ():
		if not vars().has_key('silent') or globals().has_key('silent'):
			print ('Microturbulence outside range')
		return np.array([-9,-9,-9])

		#lim temp/gravity
	if t > 6500. and g < 3.0:
		if not silent:
			print ('Minimum logg=3.0 for Teff>6500K')
		return np.array([-9,-9,-9])
	if t > 5500. and g < 2.0:
		if not silent:
			print ('Minimum logg=2.0 for Teff>5500K')
		return np.array([-9,-9,-9])
		#lim microturb/gravity
	if x > 2 and g > 3.0:
		if not silent:
			print ('Maximum microturbulence=2.0 for logg>3.0')
		return np.array([-9,-9,-9])
	
	t2=time.clock()
	
	######defines arrays with wl e wn values (r is a dictionary with common variables)######
	
	sl=np.array([[[[rwl[li,xi[0],0,gi[0],ti[0]],rwl[li,xi[0],0,gi[0],ti[1]]],[rwl[li,xi[0],0,gi[1],ti[0]],rwl[li,xi[0],0,gi[1],ti[1]]]],[[rwl[li,xi[0],1,gi[0],ti[0]],rwl[li,xi[0],1,gi[0],ti[1]]],[rwl[li,xi[0],1,gi[1],ti[0]],rwl[li,xi[0],1,gi[1],ti[1]]]],[[rwl[li,xi[0],2,gi[0],ti[0]],rwl[li,xi[0],2,gi[0],ti[1]]],[rwl[li,xi[0],2,gi[1],ti[0]],rwl[li,xi[0],2,gi[1],ti[1]]]],[[rwl[li,xi[0],3,gi[0],ti[0]],rwl[li,xi[0],3,gi[0],ti[1]]],[rwl[li,xi[0],3,gi[1],ti[0]],rwl[li,xi[0],3,gi[1],ti[1]]]],[[rwl[li,xi[0],4,gi[0],ti[0]],rwl[li,xi[0],4,gi[0],ti[1]]],[rwl[li,xi[0],4,gi[1],ti[0]],rwl[li,xi[0],4,gi[1],ti[1]]]],[[rwl[li,xi[0],5,gi[0],ti[0]],rwl[li,xi[0],5,gi[0],ti[1]]],[rwl[li,xi[0],5,gi[1],ti[0]],rwl[li,xi[0],5,gi[1],ti[1]]]],[[rwl[li,xi[0],6,gi[0],ti[0]],rwl[li,xi[0],6,gi[0],ti[1]]],[rwl[li,xi[0],6,gi[1],ti[0]],rwl[li,xi[0],6,gi[1],ti[1]]]],[[rwl[li,xi[0],7,gi[0],ti[0]],rwl[li,xi[0],7,gi[0],ti[1]]],[rwl[li,xi[0],7,gi[1],ti[0]],rwl[li,xi[0],7,gi[1],ti[1]]]],[[rwl[li,xi[0],8,gi[0],ti[0]],rwl[li,xi[0],8,gi[0],ti[1]]],[rwl[li,xi[0],8,gi[1],ti[0]],rwl[li,xi[0],8,gi[1],ti[1]]]],[[rwl[li,xi[0],9,gi[0],ti[0]],rwl[li,xi[0],9,gi[0],ti[1]]],[rwl[li,xi[0],9,gi[1],ti[0]],rwl[li,xi[0],9,gi[1],ti[1]]]],[[rwl[li,xi[0],10,gi[0],ti[0]],rwl[li,xi[0],10,gi[0],ti[1]]],[rwl[li,xi[0],10,gi[1],ti[0]],rwl[li,xi[0],10,gi[1],ti[1]]]],[[rwl[li,xi[0],11,gi[0],ti[0]],rwl[li,xi[0],11,gi[0],ti[1]]],[rwl[li,xi[0],11,gi[1],ti[0]],rwl[li,xi[0],11,gi[1],ti[1]]]],[[rwl[li,xi[0],12,gi[0],ti[0]],rwl[li,xi[0],12,gi[0],ti[1]]],[rwl[li,xi[0],12,gi[1],ti[0]],rwl[li,xi[0],12,gi[1],ti[1]]]],[[rwl[li,xi[0],13,gi[0],ti[0]],rwl[li,xi[0],13,gi[0],ti[1]]],[rwl[li,xi[0],13,gi[1],ti[0]],rwl[li,xi[0],13,gi[1],ti[1]]]],[[rwl[li,xi[0],14,gi[0],ti[0]],rwl[li,xi[0],14,gi[0],ti[1]]],[rwl[li,xi[0],14,gi[1],ti[0]],rwl[li,xi[0],14,gi[1],ti[1]]]],[[rwl[li,xi[0],15,gi[0],ti[0]],rwl[li,xi[0],15,gi[0],ti[1]]],[rwl[li,xi[0],15,gi[1],ti[0]],rwl[li,xi[0],15,gi[1],ti[1]]]],[[rwl[li,xi[0],16,gi[0],ti[0]],rwl[li,xi[0],16,gi[0],ti[1]]],[rwl[li,xi[0],16,gi[1],ti[0]],rwl[li,xi[0],16,gi[1],ti[1]]]],[[rwl[li,xi[0],17,gi[0],ti[0]],rwl[li,xi[0],17,gi[0],ti[1]]],[rwl[li,xi[0],17,gi[1],ti[0]],rwl[li,xi[0],17,gi[1],ti[1]]]],[[rwl[li,xi[0],18,gi[0],ti[0]],rwl[li,xi[0],18,gi[0],ti[1]]],[rwl[li,xi[0],18,gi[1],ti[0]],rwl[li,xi[0],18,gi[1],ti[1]]]],[[rwl[li,xi[0],19,gi[0],ti[0]],rwl[li,xi[0],19,gi[0],ti[1]]],[rwl[li,xi[0],19,gi[1],ti[0]],rwl[li,xi[0],19,gi[1],ti[1]]]],[[rwl[li,xi[0],20,gi[0],ti[0]],rwl[li,xi[0],20,gi[0],ti[1]]],[rwl[li,xi[0],20,gi[1],ti[0]],rwl[li,xi[0],20,gi[1],ti[1]]]],[[rwl[li,xi[0],21,gi[0],ti[0]],rwl[li,xi[0],21,gi[0],ti[1]]],[rwl[li,xi[0],21,gi[1],ti[0]],rwl[li,xi[0],21,gi[1],ti[1]]]],[[rwl[li,xi[0],22,gi[0],ti[0]],rwl[li,xi[0],22,gi[0],ti[1]]],[rwl[li,xi[0],22,gi[1],ti[0]],rwl[li,xi[0],22,gi[1],ti[1]]]]],
[[[rwl[li,xi[1],0,gi[0],ti[0]],rwl[li,xi[1],0,gi[0],ti[1]]],[rwl[li,xi[1],0,gi[1],ti[0]],rwl[li,xi[1],0,gi[1],ti[1]]]],[[rwl[li,xi[1],1,gi[0],ti[0]],rwl[li,xi[1],1,gi[0],ti[1]]],[rwl[li,xi[1],1,gi[1],ti[0]],rwl[li,xi[1],1,gi[1],ti[1]]]],[[rwl[li,xi[1],2,gi[0],ti[0]],rwl[li,xi[1],2,gi[0],ti[1]]],[rwl[li,xi[1],2,gi[1],ti[0]],rwl[li,xi[1],2,gi[1],ti[1]]]],[[rwl[li,xi[1],3,gi[0],ti[0]],rwl[li,xi[1],3,gi[0],ti[1]]],[rwl[li,xi[1],3,gi[1],ti[0]],rwl[li,xi[1],3,gi[1],ti[1]]]],[[rwl[li,xi[1],4,gi[0],ti[0]],rwl[li,xi[1],4,gi[0],ti[1]]],[rwl[li,xi[1],4,gi[1],ti[0]],rwl[li,xi[1],4,gi[1],ti[1]]]],[[rwl[li,xi[1],5,gi[0],ti[0]],rwl[li,xi[1],5,gi[0],ti[1]]],[rwl[li,xi[1],5,gi[1],ti[0]],rwl[li,xi[1],5,gi[1],ti[1]]]],[[rwl[li,xi[1],6,gi[0],ti[0]],rwl[li,xi[1],6,gi[0],ti[1]]],[rwl[li,xi[1],6,gi[1],ti[0]],rwl[li,xi[1],6,gi[1],ti[1]]]],[[rwl[li,xi[1],7,gi[0],ti[0]],rwl[li,xi[1],7,gi[0],ti[1]]],[rwl[li,xi[1],7,gi[1],ti[0]],rwl[li,xi[1],7,gi[1],ti[1]]]],[[rwl[li,xi[1],8,gi[0],ti[0]],rwl[li,xi[1],8,gi[0],ti[1]]],[rwl[li,xi[1],8,gi[1],ti[0]],rwl[li,xi[1],8,gi[1],ti[1]]]],[[rwl[li,xi[1],9,gi[0],ti[0]],rwl[li,xi[1],9,gi[0],ti[1]]],[rwl[li,xi[1],9,gi[1],ti[0]],rwl[li,xi[1],9,gi[1],ti[1]]]],[[rwl[li,xi[1],10,gi[0],ti[0]],rwl[li,xi[1],10,gi[0],ti[1]]],[rwl[li,xi[1],10,gi[1],ti[0]],rwl[li,xi[1],10,gi[1],ti[1]]]],[[rwl[li,xi[1],11,gi[0],ti[0]],rwl[li,xi[1],11,gi[0],ti[1]]],[rwl[li,xi[1],11,gi[1],ti[0]],rwl[li,xi[1],11,gi[1],ti[1]]]],[[rwl[li,xi[1],12,gi[0],ti[0]],rwl[li,xi[1],12,gi[0],ti[1]]],[rwl[li,xi[1],12,gi[1],ti[0]],rwl[li,xi[1],12,gi[1],ti[1]]]],[[rwl[li,xi[1],13,gi[0],ti[0]],rwl[li,xi[1],13,gi[0],ti[1]]],[rwl[li,xi[1],13,gi[1],ti[0]],rwl[li,xi[1],13,gi[1],ti[1]]]],[[rwl[li,xi[1],14,gi[0],ti[0]],rwl[li,xi[1],14,gi[0],ti[1]]],[rwl[li,xi[1],14,gi[1],ti[0]],rwl[li,xi[1],14,gi[1],ti[1]]]],[[rwl[li,xi[1],15,gi[0],ti[0]],rwl[li,xi[1],15,gi[0],ti[1]]],[rwl[li,xi[1],15,gi[1],ti[0]],rwl[li,xi[1],15,gi[1],ti[1]]]],[[rwl[li,xi[1],16,gi[0],ti[0]],rwl[li,xi[1],16,gi[0],ti[1]]],[rwl[li,xi[1],16,gi[1],ti[0]],rwl[li,xi[1],16,gi[1],ti[1]]]],[[rwl[li,xi[1],17,gi[0],ti[0]],rwl[li,xi[1],17,gi[0],ti[1]]],[rwl[li,xi[1],17,gi[1],ti[0]],rwl[li,xi[1],17,gi[1],ti[1]]]],[[rwl[li,xi[1],18,gi[0],ti[0]],rwl[li,xi[1],18,gi[0],ti[1]]],[rwl[li,xi[1],18,gi[1],ti[0]],rwl[li,xi[1],18,gi[1],ti[1]]]],[[rwl[li,xi[1],19,gi[0],ti[0]],rwl[li,xi[1],19,gi[0],ti[1]]],[rwl[li,xi[1],19,gi[1],ti[0]],rwl[li,xi[1],19,gi[1],ti[1]]]],[[rwl[li,xi[1],20,gi[0],ti[0]],rwl[li,xi[1],20,gi[0],ti[1]]],[rwl[li,xi[1],20,gi[1],ti[0]],rwl[li,xi[1],20,gi[1],ti[1]]]],[[rwl[li,xi[1],21,gi[0],ti[0]],rwl[li,xi[1],21,gi[0],ti[1]]],[rwl[li,xi[1],21,gi[1],ti[0]],rwl[li,xi[1],21,gi[1],ti[1]]]],[[rwl[li,xi[1],22,gi[0],ti[0]],rwl[li,xi[1],22,gi[0],ti[1]]],[rwl[li,xi[1],22,gi[1],ti[0]],rwl[li,xi[1],22,gi[1],ti[1]]]]]])

	sn=np.array([[[[rwn[li,xi[0],0,gi[0],ti[0]],rwn[li,xi[0],0,gi[0],ti[1]]],[rwn[li,xi[0],0,gi[1],ti[0]],rwn[li,xi[0],0,gi[1],ti[1]]]],[[rwn[li,xi[0],1,gi[0],ti[0]],rwn[li,xi[0],1,gi[0],ti[1]]],[rwn[li,xi[0],1,gi[1],ti[0]],rwn[li,xi[0],1,gi[1],ti[1]]]],[[rwn[li,xi[0],2,gi[0],ti[0]],rwn[li,xi[0],2,gi[0],ti[1]]],[rwn[li,xi[0],2,gi[1],ti[0]],rwn[li,xi[0],2,gi[1],ti[1]]]],[[rwn[li,xi[0],3,gi[0],ti[0]],rwn[li,xi[0],3,gi[0],ti[1]]],[rwn[li,xi[0],3,gi[1],ti[0]],rwn[li,xi[0],3,gi[1],ti[1]]]],[[rwn[li,xi[0],4,gi[0],ti[0]],rwn[li,xi[0],4,gi[0],ti[1]]],[rwn[li,xi[0],4,gi[1],ti[0]],rwn[li,xi[0],4,gi[1],ti[1]]]],[[rwn[li,xi[0],5,gi[0],ti[0]],rwn[li,xi[0],5,gi[0],ti[1]]],[rwn[li,xi[0],5,gi[1],ti[0]],rwn[li,xi[0],5,gi[1],ti[1]]]],[[rwn[li,xi[0],6,gi[0],ti[0]],rwn[li,xi[0],6,gi[0],ti[1]]],[rwn[li,xi[0],6,gi[1],ti[0]],rwn[li,xi[0],6,gi[1],ti[1]]]],[[rwn[li,xi[0],7,gi[0],ti[0]],rwn[li,xi[0],7,gi[0],ti[1]]],[rwn[li,xi[0],7,gi[1],ti[0]],rwn[li,xi[0],7,gi[1],ti[1]]]],[[rwn[li,xi[0],8,gi[0],ti[0]],rwn[li,xi[0],8,gi[0],ti[1]]],[rwn[li,xi[0],8,gi[1],ti[0]],rwn[li,xi[0],8,gi[1],ti[1]]]],[[rwn[li,xi[0],9,gi[0],ti[0]],rwn[li,xi[0],9,gi[0],ti[1]]],[rwn[li,xi[0],9,gi[1],ti[0]],rwn[li,xi[0],9,gi[1],ti[1]]]],[[rwn[li,xi[0],10,gi[0],ti[0]],rwn[li,xi[0],10,gi[0],ti[1]]],[rwn[li,xi[0],10,gi[1],ti[0]],rwn[li,xi[0],10,gi[1],ti[1]]]],[[rwn[li,xi[0],11,gi[0],ti[0]],rwn[li,xi[0],11,gi[0],ti[1]]],[rwn[li,xi[0],11,gi[1],ti[0]],rwn[li,xi[0],11,gi[1],ti[1]]]],[[rwn[li,xi[0],12,gi[0],ti[0]],rwn[li,xi[0],12,gi[0],ti[1]]],[rwn[li,xi[0],12,gi[1],ti[0]],rwn[li,xi[0],12,gi[1],ti[1]]]],[[rwn[li,xi[0],13,gi[0],ti[0]],rwn[li,xi[0],13,gi[0],ti[1]]],[rwn[li,xi[0],13,gi[1],ti[0]],rwn[li,xi[0],13,gi[1],ti[1]]]],[[rwn[li,xi[0],14,gi[0],ti[0]],rwn[li,xi[0],14,gi[0],ti[1]]],[rwn[li,xi[0],14,gi[1],ti[0]],rwn[li,xi[0],14,gi[1],ti[1]]]],[[rwn[li,xi[0],15,gi[0],ti[0]],rwn[li,xi[0],15,gi[0],ti[1]]],[rwn[li,xi[0],15,gi[1],ti[0]],rwn[li,xi[0],15,gi[1],ti[1]]]],[[rwn[li,xi[0],16,gi[0],ti[0]],rwn[li,xi[0],16,gi[0],ti[1]]],[rwn[li,xi[0],16,gi[1],ti[0]],rwn[li,xi[0],16,gi[1],ti[1]]]],[[rwn[li,xi[0],17,gi[0],ti[0]],rwn[li,xi[0],17,gi[0],ti[1]]],[rwn[li,xi[0],17,gi[1],ti[0]],rwn[li,xi[0],17,gi[1],ti[1]]]],[[rwn[li,xi[0],18,gi[0],ti[0]],rwn[li,xi[0],18,gi[0],ti[1]]],[rwn[li,xi[0],18,gi[1],ti[0]],rwn[li,xi[0],18,gi[1],ti[1]]]],[[rwn[li,xi[0],19,gi[0],ti[0]],rwn[li,xi[0],19,gi[0],ti[1]]],[rwn[li,xi[0],19,gi[1],ti[0]],rwn[li,xi[0],19,gi[1],ti[1]]]],[[rwn[li,xi[0],20,gi[0],ti[0]],rwn[li,xi[0],20,gi[0],ti[1]]],[rwn[li,xi[0],20,gi[1],ti[0]],rwn[li,xi[0],20,gi[1],ti[1]]]],[[rwn[li,xi[0],21,gi[0],ti[0]],rwn[li,xi[0],21,gi[0],ti[1]]],[rwn[li,xi[0],21,gi[1],ti[0]],rwn[li,xi[0],21,gi[1],ti[1]]]],[[rwn[li,xi[0],22,gi[0],ti[0]],rwn[li,xi[0],22,gi[0],ti[1]]],[rwn[li,xi[0],22,gi[1],ti[0]],rwn[li,xi[0],22,gi[1],ti[1]]]]],
[[[rwn[li,xi[1],0,gi[0],ti[0]],rwn[li,xi[1],0,gi[0],ti[1]]],[rwn[li,xi[1],0,gi[1],ti[0]],rwn[li,xi[1],0,gi[1],ti[1]]]],[[rwn[li,xi[1],1,gi[0],ti[0]],rwn[li,xi[1],1,gi[0],ti[1]]],[rwn[li,xi[1],1,gi[1],ti[0]],rwn[li,xi[1],1,gi[1],ti[1]]]],[[rwn[li,xi[1],2,gi[0],ti[0]],rwn[li,xi[1],2,gi[0],ti[1]]],[rwn[li,xi[1],2,gi[1],ti[0]],rwn[li,xi[1],2,gi[1],ti[1]]]],[[rwn[li,xi[1],3,gi[0],ti[0]],rwn[li,xi[1],3,gi[0],ti[1]]],[rwn[li,xi[1],3,gi[1],ti[0]],rwn[li,xi[1],3,gi[1],ti[1]]]],[[rwn[li,xi[1],4,gi[0],ti[0]],rwn[li,xi[1],4,gi[0],ti[1]]],[rwn[li,xi[1],4,gi[1],ti[0]],rwn[li,xi[1],4,gi[1],ti[1]]]],[[rwn[li,xi[1],5,gi[0],ti[0]],rwn[li,xi[1],5,gi[0],ti[1]]],[rwn[li,xi[1],5,gi[1],ti[0]],rwn[li,xi[1],5,gi[1],ti[1]]]],[[rwn[li,xi[1],6,gi[0],ti[0]],rwn[li,xi[1],6,gi[0],ti[1]]],[rwn[li,xi[1],6,gi[1],ti[0]],rwn[li,xi[1],6,gi[1],ti[1]]]],[[rwn[li,xi[1],7,gi[0],ti[0]],rwn[li,xi[1],7,gi[0],ti[1]]],[rwn[li,xi[1],7,gi[1],ti[0]],rwn[li,xi[1],7,gi[1],ti[1]]]],[[rwn[li,xi[1],8,gi[0],ti[0]],rwn[li,xi[1],8,gi[0],ti[1]]],[rwn[li,xi[1],8,gi[1],ti[0]],rwn[li,xi[1],8,gi[1],ti[1]]]],[[rwn[li,xi[1],9,gi[0],ti[0]],rwn[li,xi[1],9,gi[0],ti[1]]],[rwn[li,xi[1],9,gi[1],ti[0]],rwn[li,xi[1],9,gi[1],ti[1]]]],[[rwn[li,xi[1],10,gi[0],ti[0]],rwn[li,xi[1],10,gi[0],ti[1]]],[rwn[li,xi[1],10,gi[1],ti[0]],rwn[li,xi[1],10,gi[1],ti[1]]]],[[rwn[li,xi[1],11,gi[0],ti[0]],rwn[li,xi[1],11,gi[0],ti[1]]],[rwn[li,xi[1],11,gi[1],ti[0]],rwn[li,xi[1],11,gi[1],ti[1]]]],[[rwn[li,xi[1],12,gi[0],ti[0]],rwn[li,xi[1],12,gi[0],ti[1]]],[rwn[li,xi[1],12,gi[1],ti[0]],rwn[li,xi[1],12,gi[1],ti[1]]]],[[rwn[li,xi[1],13,gi[0],ti[0]],rwn[li,xi[1],13,gi[0],ti[1]]],[rwn[li,xi[1],13,gi[1],ti[0]],rwn[li,xi[1],13,gi[1],ti[1]]]],[[rwn[li,xi[1],14,gi[0],ti[0]],rwn[li,xi[1],14,gi[0],ti[1]]],[rwn[li,xi[1],14,gi[1],ti[0]],rwn[li,xi[1],14,gi[1],ti[1]]]],[[rwn[li,xi[1],15,gi[0],ti[0]],rwn[li,xi[1],15,gi[0],ti[1]]],[rwn[li,xi[1],15,gi[1],ti[0]],rwn[li,xi[1],15,gi[1],ti[1]]]],[[rwn[li,xi[1],16,gi[0],ti[0]],rwn[li,xi[1],16,gi[0],ti[1]]],[rwn[li,xi[1],16,gi[1],ti[0]],rwn[li,xi[1],16,gi[1],ti[1]]]],[[rwn[li,xi[1],17,gi[0],ti[0]],rwn[li,xi[1],17,gi[0],ti[1]]],[rwn[li,xi[1],17,gi[1],ti[0]],rwn[li,xi[1],17,gi[1],ti[1]]]],[[rwn[li,xi[1],18,gi[0],ti[0]],rwn[li,xi[1],18,gi[0],ti[1]]],[rwn[li,xi[1],18,gi[1],ti[0]],rwn[li,xi[1],18,gi[1],ti[1]]]],[[rwn[li,xi[1],19,gi[0],ti[0]],rwn[li,xi[1],19,gi[0],ti[1]]],[rwn[li,xi[1],19,gi[1],ti[0]],rwn[li,xi[1],19,gi[1],ti[1]]]],[[rwn[li,xi[1],20,gi[0],ti[0]],rwn[li,xi[1],20,gi[0],ti[1]]],[rwn[li,xi[1],20,gi[1],ti[0]],rwn[li,xi[1],20,gi[1],ti[1]]]],[[rwn[li,xi[1],21,gi[0],ti[0]],rwn[li,xi[1],21,gi[0],ti[1]]],[rwn[li,xi[1],21,gi[1],ti[0]],rwn[li,xi[1],21,gi[1],ti[1]]]],[[rwn[li,xi[1],22,gi[0],ti[0]],rwn[li,xi[1],22,gi[0],ti[1]]],[rwn[li,xi[1],22,gi[1],ti[0]],rwn[li,xi[1],22,gi[1],ti[1]]]]]])
	
	t3=time.clock()
	nr=len(mg)
	
	#verify if all entries are -9
	if np.max(sl)==-9 or np.max(sn)==-9:
		if not silent:
			print ('Model missing from grid or not enough data points')
		return np.array([-9,-9,-9])
	
	#remove -9 entries
	dum=0
	for i in range(nr):
		c=np.minimum(sl[:,0,:,:],sn[:,0,:,:])==-9
		if tuple(np.where(c==True)[0])!=():
			if dum >= nr-2:
				if not silent:
					print ('Model missing from grid or not enough data points')
				return np.array([-9,-9,-9])
			sl=sl[:,1:nr-dum,:,:]
			sn=sn[:,1:nr-dum,:,:]
			mg=mg[1:nr-dum]
			dum=dum+1
		d=np.minimum(sl[:,nr-dum-1,:,:],sn[:,nr-dum-1,:,:])==-9
		if tuple(np.where(d==True)[0])!=():
			if dum >= nr-2:
				if not silent:
					print ('Model missing from grid or not enough data points')
				return np.array([-9,-9,-9])
			sl=sl[:,0:nr-dum-1,:,:]
			sn=sn[:,0:nr-dum-1,:,:]
			mg=mg[0:nr-dum-1]
			dum=dum+1
	nr=nr-dum
	

	#######metallicity index#####
	fi=find_index(mg,f)
	if fi == ():
		if not silent:
			print ('Metallicity outside range')

		return np.array([-9,-9,-9])


	#######interpolation#######
	#temp eff interpolation x8	
	tl=np.zeros((2,nr,2))
	tn=np.zeros((2,nr,2))	
	if ti[1] == ti[0]:
		l=0
	else:
		l=(t-rtg[ti[0]])/(rtg[ti[1]]-rtg[ti[0]])

	for k in range(0,2):
		for m in range(0,2):
			tl[m,:,k]=sl[m,:,k,0]+l*(sl[m,:,k,1]-sl[m,:,k,0])
			tn[m,:,k]=sn[m,:,k,0]+l*(sn[m,:,k,1]-sn[m,:,k,0])
	
	#surf grav interpolation x4
	gl=np.zeros((2,nr))
	gn=np.zeros((2,nr))
	if gi[1] == gi[0]:
		l=0
	else:
		l=(g-rgg[gi[0]])/(rgg[gi[1]]-rgg[gi[0]])
	for m in range(0,2):
		gl[m,:]=tl[m,:,0]+l*(tl[m,:,1]-tl[m,:,0])
		gn[m,:]=tn[m,:,0]+l*(tn[m,:,1]-tn[m,:,0])
	
	#microturb interpolation x2
	xl=np.zeros(nr)
	xn=np.zeros(nr)
	if xi[1] == xi[0]:
		l=0
	else:
		l=(x-rxg[xi[0]])/(rxg[xi[1]]-rxg[xi[0]])
	xl=gl[0,:]+l*(gl[1,:]-gl[0,:])
	xn=gn[0,:]+l*(gn[1,:]-gn[0,:])

	#######LTE########
	#given abund LTE (al) --> find EW from LTE curve-of-growth
	if al:
		if fi[1] == fi[0]:
			l=0
		else:
			l=(f-mg[fi[0]])/(mg[fi[1]]-mg[fi[0]])
		al=f
		e=10**(xl[fi[0]]+l*(xl[fi[1]]-xl[fi[0]]))

	#otherwise, curve-of-growth --> LTE abund
	else:
		il=find_index(xl,np.log10(e))
		if il == ():
			if not silent:
				print ('Equivalent width outside range of LTE curve-of-growth')
			al=-9
		else:
			if il[0] == il[1]:
				l=0
			else:
				l=(np.log10(e)-xl[il[0]])/(xl[il[1]]-xl[il[0]])
			al=mg[il[0]]+l*(mg[il[1]]-mg[il[0]])
	

	#######NLTE#######
	#curve-of-growth --> NLTE abund
	inn =find_index(xn,np.log10(e))
	if inn == ():
		if not silent:
			print ('Equivalent width outside range of NLTE curve-of-growth')
		an=-9
	else:
		if inn[0] == inn[1]:
			l=0
		else:
			l=(np.log10(e)-xn[inn[0]])/(xn[inn[1]]-xn[inn[0]])
		an=mg[inn[0]]+l*(mg[inn[1]]-mg[inn[0]])

	

	#final outputs
	if al == -9 or an == -9:
		co=-9
	else:
		co=an-al

	t4=time.clock()
	return [al,an,co]
	#[t1-t0,t2-t1,t3-t2,t4-t3,t4-t0]


