
# coding=utf-8
import numpy as np
import inspect as ip
import scipy.io as io

def find_index(y,x): #y,x sao arrays
	ii=np.where(np.absolute(y-x) < 1*10**(-8)) #tuple (array([indices]),)
	i=tuple(ii[0]) #tuple indices q satisfazem cond

	if i != (): #caso hajam indices q satisfaçam cond
		i=[i,i]
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
			i=np.sort(i) #ordenar ind

	return i

##########################################################################
def iron_nlte(e,t,g,f,x,w,al=al,silent=silent):
	
	#####verificar parametros dados#####
	if len(tuple(ip.getargspec(iron_nlte)[0])) != 8:
		print ('CALLING SEQUENCE:\n	a=iron_nlte(e,t,g,f,x,w,/al) \nINPUTS: \n       e          [0.1,500]       Equivalent width [pm] (optional)\n       t          [4000.0,8000.0] Effective temperature [K])\n       g          [1.0,5.0]       Logarithm of surface gravity [cgs]\n       f          [-5.0,0.5]      Metallicity [Fe/H] (LTE)\n       x          [1,5]           Microturbulence [km/s]\n       w          [0,3345]        Line index\n\n       al         [0,1]           If flag is set, f is fixed and e\n                                  returned (optional)\n')                                                 
		return [-9,-9,-9]
	
	######chamar variaveis comuns######
	r=io.readsav('/home/pedrosobral/PEEC/NLTE/iron_grid.sav')
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
	
	mg,f=rfg+7.45,f+7.45
	
	#####encontrar indices de temp, surf grav e microturb#####
	ti=find_index(rtg,t)
	gi=find_index(rgg,g)
	xi=find_index(rxg,x)
	li=w
	
	######info sobre a linha #######
	if not vars().has_key('silent') or globals().has_key('silent'):
		print ('Using calculations for %8.3f nm, EV_low= %7.3f eV, log(gf)= %7.3f' % (r.get('wv')[li],r.get('el')[li],np.log10(r.get('gf')[li])))

	######verificar se parametros estao dentro do intervalo permitido######
		#equiv width	
	if not vars().has_key('al') or globals().has_key('al'):
		if e < 0.1 or e > 100:
			if not vars().has_key('silent') or globals().has_key('silent'):
				print ('Equivalent width outside range')
			return [-9,-9,-9]
	
		#eff temp
	if ti == ():
		if not vars().has_key('silent') or globals().has_key('silent'):
			print ('Effective temperature outside range')
		return np.array([-9,-9,-9])

		#line index
	if li < 0 or li > 3345:
		if not vars().has_key('silent') or globals().has_key('silent'):
			print ('Line index outside range')
		return np.array([-9,-9,-9])

		#surf gravity
	if gi == ():
		if not vars().has_key('silent') or globals().has_key('silent'):
			print ('Surface gravity outside range')
		return np.array([-9,-9,-9])

		#microturb
	if xi == ():
		if not vars().has_key('silent') or globals().has_key('silent'):
			print ('Microturbulence outside range')
		return np.array([-9,-9,-9])

		#lim temp/gravity
	if t > 6500. and g < 3.0:
		if not vars().has_key('silent') or globals().has_key('silent'):
			print ('Minimum logg=3.0 for Teff>6500K')
		return np.array([-9,-9,-9])
	if t > 5500. and g < 2.0:
		if not vars().has_key('silent') or globals().has_key('silent'):
			print ('Minimum logg=2.0 for Teff>5500K')
		return np.array([-9,-9,-9])
		#lim microturb/gravity
	if x > 2 and g > 3.0:
		if not vars().has_key('silent') or globals().has_key('silent'):
			print ('Maximum microturbulence=2.0 for logg>3.0')
		return np.array([-9,-9,-9])
	

	
	######definir arrays c/ valores de wl e wn (r é dict de var comuns)######
	
	sl=rwl[li,[xi[0],xi[1]],:,[gi[0],gi[1]],[ti[0],ti[1]]]
	sn=rwn[li,[xi[0],xi[1]],:,[gi[0],gi[1]],[ti[0],ti[1]]]
	nr=len(mg)

	
	######verificar valores de sl e sn######
	#funcoes para verificar se indices estao correctos
	def erro_sl():
		try:
			sl
		except IndexError as e:
			print (e)
	def erro_sn():
		try:
			sn
		except IndexError as e:
			print (e)

	def erro_sl1():
		try:
			sl[:,:,0,:]
		except IndexError as e:
			print (e)
	def erro_sn1():
		try:
			sn[:,:,0,:]
		except IndexError as e:
			print (e)
	def erro_sl2():
		try:
			sl[:,:,1:nr-dum-1,:]
		except IndexError as e:
			print (e)
	def erro_sn2():
		try:
			sn[:,:,1:nr-dum-1,:]
		except IndexError as e:
			print (e)

	#verificar entradas
	if erro_sn() or erro_sl() != None:
		def outofrange():
			if not vars().has_key('silent') or globals().has_key('silent'):	
				print ('Model missing from grid or not enough data points')
			return np.array([-9,-9,-9])
	
	#remover -9
	dum=0
	for i in range(nr):
		if erro_sl1() or erro_sn1() != None:
			if dum >= nr-2:
				outofrange()
			sl=sl[:,:,1:nr-dum-1,:]
			sn=sn[:,:,1:nr-dum-1,:]
			mg=mg[1:nr-dum-1]
			dum=dum+1
		if erro_sl2() or erro_sn2() != None:
			if dum >= nr-2:
				outofrange()
			sl=sl[:,:,0:nr-dum-2,:]
			sn=sn[:,:,0:nr-dum-2,:]
			mg=mg[0:nr-dum-2]
			dum=dum+1
	nr=nr-dum
	

	#######indice da metalicidade#####
	fi=find_index(mg,f)

	if fi[0] == ():
		if not vars().has_key('silent') or globals().has_key('silent'):
			print ('Metallicity outside range')

			return np.array([-9,-9,-9])


	#######interpolacoes#######
	#interpolação da temp eff x8	
	tl=np.zeros((2,nr,2))
	tn=np.zeros((2,nr,2))
	if ti[1] == ti[0]:
		l=0
	else:
		l=(t-rtg[ti[0]])/(rtg[ti[1]]-rtg[ti[0]])

	for k in range(0,2):
		for m in range(0,2):
			tl[k,:,m]=sl[0,k,:,m]+l*(sl[1,k,:,m]-sl[0,k,:,m])
			tn[k,:,m]=sn[0,k,:,m]+l*(sn[1,k,:,m]-sn[0,k,:,m])
	
	#interpolaçao surf grav x4
	gl=np.zeros((nr,2))
	gn=np.zeros((nr,2))
	if gi[1] == gi[0]:
		l=0
	else:
		l=(g-rgg[gi[0]])/(rgg[gi[1]]-rgg[gi[0]])
	for m in range(0,2):
		gl[:,m]=tl[0,:,m]+l*(tl[1,:,m]-tl[0,:,m])
		gn[:,m]=tn[0,:,m]+l*(tn[1,:,m]-tn[0,:,m])
	
	#interpolaçao microturb x2
	xl=np.zeros(nr)
	xn=np.zeros(nr)
	if xi[1] == xi[0]:
		l=0
	else:
		l=(x-rxg[xi[0]])/(rxg[xi[1]]-rxg[xi[0]])
	xl=gl[:,0]+l*(gl[:,1]-gl[:,0])
	xn=gn[:,0]+l*(gn[:,1]-gn[:,0])


	#######LTE########
	#abund LTE dada (al) --> encontrar largura equiv da curva de crescimento LTE
	if vars().has_key('al') or globals().has_key('al'):
		if fi[1] == fi[0]:
			l=0
		else:
			l=(f-mg[fi[0]])/(mg[fi[1]]-mg[fi[0]])
		al=f
		e=10**(xl[fi[0]]+l*(xl[fi[1]]-xl[fi[0]]))

	#caso contrario, curva de crescimento --> abund LTE
	else:
		il=find_index(xl,np.log10(e))
		if il[0] == ():
			if not vars().has_key('silent') or globals().has_key('silent'):
				print ('Equivalent width outside range of LTE curve-of-growth')
			al=-9
		else:
			if il[0] == il[1]:
				l=0
			else:
				l=(np.log10(e)-xl[il[0]])/(xl[il[1]]-xl[il[0]])
			al=mg[il[0]]+l*(mg[il[1]]-mg[il[0]])
	

	#######NLTE#######
	#curva de crescim --> abund NLTE
	inn =find_index(xn,np.log10(e))
	if inn[0] == ():
		if not vars().has_key('silent') or globals().has_key('silent'):
			print ('Equivalent width outside range of NLTE curve-of-growth')
		an=-9
	else:
		if inn[0] == inn[1]:
			l=0
		else:
			l=(np.log10(e)-xn[inn[0]])/(xn[inn[1]]-xn[inn[0]])
		an=mg[inn[0]]+l*(mg[inn[1]]-mg[inn[0]])

	

	#outputs finais
	if al == -9 or an == -9:
		co=-9
	else:
		co=an-al

	return [al,an,co]


