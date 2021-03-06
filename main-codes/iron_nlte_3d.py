
# coding=utf-8
import numpy as np
import inspect as ip
import scipy.io as io

def find_index(y,x): #y,x sao arrays
	ii=np.where(np.absolute(y-x) < 1e-8) #tuple (array([indices]),)
	i=tuple(ii[0]) #tuple index satisfying the condition

	if i != (): #in case that exist indices satistying the condition
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
			i=np.sort(i) #index arrangement

	return i

##########################################################################

#FUNCTION iron_nlte_3d:
#
#	it allows the calculation of LTE/NLTE abundances for a given neutral iron EW, using linear interpolation, for several stars.
#
#
#INPUTS (arrays): 
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
silent=True #False => prints everything


#ATENTION: if inputs are not in the grid, the script adds co=-9 to co_tot

def iron_nlte_3d(e,t,g,f,w,al=al,silent=silent):
	'semelhante a iron_nlte mas agora admite inputs de t,g ou f em forma de array. Apenas 2 de cada vez'
	'retorna grid com diferenças das abundâncias'
	
	#####verificar parametros dados#####
	if len(tuple(ip.getargspec(iron_nlte_3d)[0])) != 7:
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
	
	f=f+7.45

	#criar arrays para ser possivel avaliar quais sao apenas de 1 nr	
	t=np.array(t)
	g=np.array(g)
	f=np.array(f)
	
	
	#avaliar quais sao de apenas 1 nr e criar nr de linhas (horiz) e colunas (vert)
	if f.size==1:
		vert=t.size
		horiz=g.size
		T,G=np.meshgrid(t,g)	

	elif g.size==1:
		vert=t.size
		horiz=f.size
		T,F=np.meshgrid(t,f)

	elif t.size==1:
		vert=g.size
		horiz=f.size
		G,F=np.meshgrid(g,f)

	
	######criar variaveis q acumulam outputs######
	al_tot=np.zeros((horiz,vert))
	an_tot=np.zeros((horiz,vert))
	co_tot=np.zeros((horiz,vert))


	#criar grid e percorrer arrays de cada variavel de input 
	for i_vert in range(vert):#escolhe a coluna
		for j_horiz in range(horiz):#escolhe a linha
	
			####quando f é valor unico###
			if f.size==1: #encontrar indices de temp, surf grav e metal#
				t=T[j_horiz][i_vert]
				g=G[j_horiz][i_vert]
				f=f
				ti=find_index(rtg,t)
				gi=find_index(rgg,g)
				

			####quando g é valor unico####
			elif g.size==1: #encontrar indices de temp, surf grav e metal#
				t=[j_horiz][i_vert]
				g=g
				f=[j_horiz][i_vert]
				ti=find_index(rtg,t)
				gi=find_index(rgg,g)
				
					
			#####quando t é valor unico####
			elif t.size==1: #encontrar indices de temp, surf grav e metal#
				t=t
				g=G[j_horiz][i_vert]
				f=F[j_horiz][i_vert]
				ti=find_index(rtg,t)
				gi=find_index(rtg,g)


			#relaçao entre g e x
			if g>4:
				x=1
			else:
				x=2
			

			#mg,indice risca e indice metal
			mg=rfg+7.45
			li=w
			xi=find_index(rxg,x)


			######info sobre a linha #######
			if not silent:
				print ('Using calculations for %8.3f nm, EV_low= %7.3f eV, log(gf)= %7.3f' % (r.get('wv')[li],r.get('el')[li],np.log10(r.get('gf')[li])))



			######verificar se parametros estao dentro do intervalo permitido######
			#equiv width	
			if not silent:
				if e < 0.1 or e > 100:
					if not silent:
						print ('Equivalent width outside range')
					al_tot[j_horiz][i_vert]=-9
					an_tot[j_horiz][i_vert]=-9
					co_tot[j_horiz][i_vert]=-9						
					continue
				#eff temp
			if ti == ():
				if not silent:
					print ('Effective temperature outside range')
				al_tot[j_horiz][i_vert]=-9
				an_tot[j_horiz][i_vert]=-9
				co_tot[j_horiz][i_vert]=-9						
				continue
				#line index
			if li < 0 or li > 3345:
				if not silent:
					print ('Line index outside range')
				al_tot[j_horiz][i_vert]=-9
				an_tot[j_horiz][i_vert]=-9
				co_tot[j_horiz][i_vert]=-9
				#surf gravity
			if gi == ():
				if not silent:
					print ('Surface gravity outside range')
				al_tot[j_horiz][i_vert]=-9
				an_tot[j_horiz][i_vert]=-9
				co_tot[j_horiz][i_vert]=-9						
				continue
				#microturb
			if xi == ():
				if not vars().has_key('silent') or globals().has_key('silent'):
					print ('Microturbulence outside range')
				al_tot[j_horiz][i_vert]=-9
				an_tot[j_horiz][i_vert]=-9
				co_tot[j_horiz][i_vert]=-9						
				continue
				#lim temp/gravity
			if t > 6500. and g < 3.0:
				if not silent:
					print ('Minimum logg=3.0 for Teff>6500K')
				al_tot[j_horiz][i_vert]=-9
				an_tot[j_horiz][i_vert]=-9
				co_tot[j_horiz][i_vert]=-9
				continue						
			if t > 5500. and g < 2.0:
				if not silent:
					print ('Minimum logg=2.0 for Teff>5500K')
				al_tot[j_horiz][i_vert]=-9
				an_tot[j_horiz][i_vert]=-9
				co_tot[j_horiz][i_vert]=-9
				continue						
				#lim microturb/gravity
			if x > 2 and g > 3.0:
				if not silent:
					print ('Maximum microturbulence=2.0 for logg>3.0')
				al_tot[j_horiz][i_vert]=-9
				an_tot[j_horiz][i_vert]=-9
				co_tot[j_horiz][i_vert]=-9					
				continue

	
			######definir arrays c/ valores de wl e wn (r é dict de var comuns)######
	
			sl=np.array([[[[rwl[li,xi[0],0,gi[0],ti[0]],rwl[li,xi[0],0,gi[0],ti[1]]],[rwl[li,xi[0],0,gi[1],ti[0]],rwl[li,xi[0],0,gi[1],ti[1]]]],[[rwl[li,xi[0],1,gi[0],ti[0]],rwl[li,xi[0],1,gi[0],ti[1]]],[rwl[li,xi[0],1,gi[1],ti[0]],rwl[li,xi[0],1,gi[1],ti[1]]]],[[rwl[li,xi[0],2,gi[0],ti[0]],rwl[li,xi[0],2,gi[0],ti[1]]],[rwl[li,xi[0],2,gi[1],ti[0]],rwl[li,xi[0],2,gi[1],ti[1]]]],[[rwl[li,xi[0],3,gi[0],ti[0]],rwl[li,xi[0],3,gi[0],ti[1]]],[rwl[li,xi[0],3,gi[1],ti[0]],rwl[li,xi[0],3,gi[1],ti[1]]]],[[rwl[li,xi[0],4,gi[0],ti[0]],rwl[li,xi[0],4,gi[0],ti[1]]],[rwl[li,xi[0],4,gi[1],ti[0]],rwl[li,xi[0],4,gi[1],ti[1]]]],[[rwl[li,xi[0],5,gi[0],ti[0]],rwl[li,xi[0],5,gi[0],ti[1]]],[rwl[li,xi[0],5,gi[1],ti[0]],rwl[li,xi[0],5,gi[1],ti[1]]]],[[rwl[li,xi[0],6,gi[0],ti[0]],rwl[li,xi[0],6,gi[0],ti[1]]],[rwl[li,xi[0],6,gi[1],ti[0]],rwl[li,xi[0],6,gi[1],ti[1]]]],[[rwl[li,xi[0],7,gi[0],ti[0]],rwl[li,xi[0],7,gi[0],ti[1]]],[rwl[li,xi[0],7,gi[1],ti[0]],rwl[li,xi[0],7,gi[1],ti[1]]]],[[rwl[li,xi[0],8,gi[0],ti[0]],rwl[li,xi[0],8,gi[0],ti[1]]],[rwl[li,xi[0],8,gi[1],ti[0]],rwl[li,xi[0],8,gi[1],ti[1]]]],[[rwl[li,xi[0],9,gi[0],ti[0]],rwl[li,xi[0],9,gi[0],ti[1]]],[rwl[li,xi[0],9,gi[1],ti[0]],rwl[li,xi[0],9,gi[1],ti[1]]]],[[rwl[li,xi[0],10,gi[0],ti[0]],rwl[li,xi[0],10,gi[0],ti[1]]],[rwl[li,xi[0],10,gi[1],ti[0]],rwl[li,xi[0],10,gi[1],ti[1]]]],[[rwl[li,xi[0],11,gi[0],ti[0]],rwl[li,xi[0],11,gi[0],ti[1]]],[rwl[li,xi[0],11,gi[1],ti[0]],rwl[li,xi[0],11,gi[1],ti[1]]]],[[rwl[li,xi[0],12,gi[0],ti[0]],rwl[li,xi[0],12,gi[0],ti[1]]],[rwl[li,xi[0],12,gi[1],ti[0]],rwl[li,xi[0],12,gi[1],ti[1]]]],[[rwl[li,xi[0],13,gi[0],ti[0]],rwl[li,xi[0],13,gi[0],ti[1]]],[rwl[li,xi[0],13,gi[1],ti[0]],rwl[li,xi[0],13,gi[1],ti[1]]]],[[rwl[li,xi[0],14,gi[0],ti[0]],rwl[li,xi[0],14,gi[0],ti[1]]],[rwl[li,xi[0],14,gi[1],ti[0]],rwl[li,xi[0],14,gi[1],ti[1]]]],[[rwl[li,xi[0],15,gi[0],ti[0]],rwl[li,xi[0],15,gi[0],ti[1]]],[rwl[li,xi[0],15,gi[1],ti[0]],rwl[li,xi[0],15,gi[1],ti[1]]]],[[rwl[li,xi[0],16,gi[0],ti[0]],rwl[li,xi[0],16,gi[0],ti[1]]],[rwl[li,xi[0],16,gi[1],ti[0]],rwl[li,xi[0],16,gi[1],ti[1]]]],[[rwl[li,xi[0],17,gi[0],ti[0]],rwl[li,xi[0],17,gi[0],ti[1]]],[rwl[li,xi[0],17,gi[1],ti[0]],rwl[li,xi[0],17,gi[1],ti[1]]]],[[rwl[li,xi[0],18,gi[0],ti[0]],rwl[li,xi[0],18,gi[0],ti[1]]],[rwl[li,xi[0],18,gi[1],ti[0]],rwl[li,xi[0],18,gi[1],ti[1]]]],[[rwl[li,xi[0],19,gi[0],ti[0]],rwl[li,xi[0],19,gi[0],ti[1]]],[rwl[li,xi[0],19,gi[1],ti[0]],rwl[li,xi[0],19,gi[1],ti[1]]]],[[rwl[li,xi[0],20,gi[0],ti[0]],rwl[li,xi[0],20,gi[0],ti[1]]],[rwl[li,xi[0],20,gi[1],ti[0]],rwl[li,xi[0],20,gi[1],ti[1]]]],[[rwl[li,xi[0],21,gi[0],ti[0]],rwl[li,xi[0],21,gi[0],ti[1]]],[rwl[li,xi[0],21,gi[1],ti[0]],rwl[li,xi[0],21,gi[1],ti[1]]]],[[rwl[li,xi[0],22,gi[0],ti[0]],rwl[li,xi[0],22,gi[0],ti[1]]],[rwl[li,xi[0],22,gi[1],ti[0]],rwl[li,xi[0],22,gi[1],ti[1]]]]],
[[[rwl[li,xi[1],0,gi[0],ti[0]],rwl[li,xi[1],0,gi[0],ti[1]]],[rwl[li,xi[1],0,gi[1],ti[0]],rwl[li,xi[1],0,gi[1],ti[1]]]],[[rwl[li,xi[1],1,gi[0],ti[0]],rwl[li,xi[1],1,gi[0],ti[1]]],[rwl[li,xi[1],1,gi[1],ti[0]],rwl[li,xi[1],1,gi[1],ti[1]]]],[[rwl[li,xi[1],2,gi[0],ti[0]],rwl[li,xi[1],2,gi[0],ti[1]]],[rwl[li,xi[1],2,gi[1],ti[0]],rwl[li,xi[1],2,gi[1],ti[1]]]],[[rwl[li,xi[1],3,gi[0],ti[0]],rwl[li,xi[1],3,gi[0],ti[1]]],[rwl[li,xi[1],3,gi[1],ti[0]],rwl[li,xi[1],3,gi[1],ti[1]]]],[[rwl[li,xi[1],4,gi[0],ti[0]],rwl[li,xi[1],4,gi[0],ti[1]]],[rwl[li,xi[1],4,gi[1],ti[0]],rwl[li,xi[1],4,gi[1],ti[1]]]],[[rwl[li,xi[1],5,gi[0],ti[0]],rwl[li,xi[1],5,gi[0],ti[1]]],[rwl[li,xi[1],5,gi[1],ti[0]],rwl[li,xi[1],5,gi[1],ti[1]]]],[[rwl[li,xi[1],6,gi[0],ti[0]],rwl[li,xi[1],6,gi[0],ti[1]]],[rwl[li,xi[1],6,gi[1],ti[0]],rwl[li,xi[1],6,gi[1],ti[1]]]],[[rwl[li,xi[1],7,gi[0],ti[0]],rwl[li,xi[1],7,gi[0],ti[1]]],[rwl[li,xi[1],7,gi[1],ti[0]],rwl[li,xi[1],7,gi[1],ti[1]]]],[[rwl[li,xi[1],8,gi[0],ti[0]],rwl[li,xi[1],8,gi[0],ti[1]]],[rwl[li,xi[1],8,gi[1],ti[0]],rwl[li,xi[1],8,gi[1],ti[1]]]],[[rwl[li,xi[1],9,gi[0],ti[0]],rwl[li,xi[1],9,gi[0],ti[1]]],[rwl[li,xi[1],9,gi[1],ti[0]],rwl[li,xi[1],9,gi[1],ti[1]]]],[[rwl[li,xi[1],10,gi[0],ti[0]],rwl[li,xi[1],10,gi[0],ti[1]]],[rwl[li,xi[1],10,gi[1],ti[0]],rwl[li,xi[1],10,gi[1],ti[1]]]],[[rwl[li,xi[1],11,gi[0],ti[0]],rwl[li,xi[1],11,gi[0],ti[1]]],[rwl[li,xi[1],11,gi[1],ti[0]],rwl[li,xi[1],11,gi[1],ti[1]]]],[[rwl[li,xi[1],12,gi[0],ti[0]],rwl[li,xi[1],12,gi[0],ti[1]]],[rwl[li,xi[1],12,gi[1],ti[0]],rwl[li,xi[1],12,gi[1],ti[1]]]],[[rwl[li,xi[1],13,gi[0],ti[0]],rwl[li,xi[1],13,gi[0],ti[1]]],[rwl[li,xi[1],13,gi[1],ti[0]],rwl[li,xi[1],13,gi[1],ti[1]]]],[[rwl[li,xi[1],14,gi[0],ti[0]],rwl[li,xi[1],14,gi[0],ti[1]]],[rwl[li,xi[1],14,gi[1],ti[0]],rwl[li,xi[1],14,gi[1],ti[1]]]],[[rwl[li,xi[1],15,gi[0],ti[0]],rwl[li,xi[1],15,gi[0],ti[1]]],[rwl[li,xi[1],15,gi[1],ti[0]],rwl[li,xi[1],15,gi[1],ti[1]]]],[[rwl[li,xi[1],16,gi[0],ti[0]],rwl[li,xi[1],16,gi[0],ti[1]]],[rwl[li,xi[1],16,gi[1],ti[0]],rwl[li,xi[1],16,gi[1],ti[1]]]],[[rwl[li,xi[1],17,gi[0],ti[0]],rwl[li,xi[1],17,gi[0],ti[1]]],[rwl[li,xi[1],17,gi[1],ti[0]],rwl[li,xi[1],17,gi[1],ti[1]]]],[[rwl[li,xi[1],18,gi[0],ti[0]],rwl[li,xi[1],18,gi[0],ti[1]]],[rwl[li,xi[1],18,gi[1],ti[0]],rwl[li,xi[1],18,gi[1],ti[1]]]],[[rwl[li,xi[1],19,gi[0],ti[0]],rwl[li,xi[1],19,gi[0],ti[1]]],[rwl[li,xi[1],19,gi[1],ti[0]],rwl[li,xi[1],19,gi[1],ti[1]]]],[[rwl[li,xi[1],20,gi[0],ti[0]],rwl[li,xi[1],20,gi[0],ti[1]]],[rwl[li,xi[1],20,gi[1],ti[0]],rwl[li,xi[1],20,gi[1],ti[1]]]],[[rwl[li,xi[1],21,gi[0],ti[0]],rwl[li,xi[1],21,gi[0],ti[1]]],[rwl[li,xi[1],21,gi[1],ti[0]],rwl[li,xi[1],21,gi[1],ti[1]]]],[[rwl[li,xi[1],22,gi[0],ti[0]],rwl[li,xi[1],22,gi[0],ti[1]]],[rwl[li,xi[1],22,gi[1],ti[0]],rwl[li,xi[1],22,gi[1],ti[1]]]]]])

			sn=np.array([[[[rwn[li,xi[0],0,gi[0],ti[0]],rwn[li,xi[0],0,gi[0],ti[1]]],[rwn[li,xi[0],0,gi[1],ti[0]],rwn[li,xi[0],0,gi[1],ti[1]]]],[[rwn[li,xi[0],1,gi[0],ti[0]],rwn[li,xi[0],1,gi[0],ti[1]]],[rwn[li,xi[0],1,gi[1],ti[0]],rwn[li,xi[0],1,gi[1],ti[1]]]],[[rwn[li,xi[0],2,gi[0],ti[0]],rwn[li,xi[0],2,gi[0],ti[1]]],[rwn[li,xi[0],2,gi[1],ti[0]],rwn[li,xi[0],2,gi[1],ti[1]]]],[[rwn[li,xi[0],3,gi[0],ti[0]],rwn[li,xi[0],3,gi[0],ti[1]]],[rwn[li,xi[0],3,gi[1],ti[0]],rwn[li,xi[0],3,gi[1],ti[1]]]],[[rwn[li,xi[0],4,gi[0],ti[0]],rwn[li,xi[0],4,gi[0],ti[1]]],[rwn[li,xi[0],4,gi[1],ti[0]],rwn[li,xi[0],4,gi[1],ti[1]]]],[[rwn[li,xi[0],5,gi[0],ti[0]],rwn[li,xi[0],5,gi[0],ti[1]]],[rwn[li,xi[0],5,gi[1],ti[0]],rwn[li,xi[0],5,gi[1],ti[1]]]],[[rwn[li,xi[0],6,gi[0],ti[0]],rwn[li,xi[0],6,gi[0],ti[1]]],[rwn[li,xi[0],6,gi[1],ti[0]],rwn[li,xi[0],6,gi[1],ti[1]]]],[[rwn[li,xi[0],7,gi[0],ti[0]],rwn[li,xi[0],7,gi[0],ti[1]]],[rwn[li,xi[0],7,gi[1],ti[0]],rwn[li,xi[0],7,gi[1],ti[1]]]],[[rwn[li,xi[0],8,gi[0],ti[0]],rwn[li,xi[0],8,gi[0],ti[1]]],[rwn[li,xi[0],8,gi[1],ti[0]],rwn[li,xi[0],8,gi[1],ti[1]]]],[[rwn[li,xi[0],9,gi[0],ti[0]],rwn[li,xi[0],9,gi[0],ti[1]]],[rwn[li,xi[0],9,gi[1],ti[0]],rwn[li,xi[0],9,gi[1],ti[1]]]],[[rwn[li,xi[0],10,gi[0],ti[0]],rwn[li,xi[0],10,gi[0],ti[1]]],[rwn[li,xi[0],10,gi[1],ti[0]],rwn[li,xi[0],10,gi[1],ti[1]]]],[[rwn[li,xi[0],11,gi[0],ti[0]],rwn[li,xi[0],11,gi[0],ti[1]]],[rwn[li,xi[0],11,gi[1],ti[0]],rwn[li,xi[0],11,gi[1],ti[1]]]],[[rwn[li,xi[0],12,gi[0],ti[0]],rwn[li,xi[0],12,gi[0],ti[1]]],[rwn[li,xi[0],12,gi[1],ti[0]],rwn[li,xi[0],12,gi[1],ti[1]]]],[[rwn[li,xi[0],13,gi[0],ti[0]],rwn[li,xi[0],13,gi[0],ti[1]]],[rwn[li,xi[0],13,gi[1],ti[0]],rwn[li,xi[0],13,gi[1],ti[1]]]],[[rwn[li,xi[0],14,gi[0],ti[0]],rwn[li,xi[0],14,gi[0],ti[1]]],[rwn[li,xi[0],14,gi[1],ti[0]],rwn[li,xi[0],14,gi[1],ti[1]]]],[[rwn[li,xi[0],15,gi[0],ti[0]],rwn[li,xi[0],15,gi[0],ti[1]]],[rwn[li,xi[0],15,gi[1],ti[0]],rwn[li,xi[0],15,gi[1],ti[1]]]],[[rwn[li,xi[0],16,gi[0],ti[0]],rwn[li,xi[0],16,gi[0],ti[1]]],[rwn[li,xi[0],16,gi[1],ti[0]],rwn[li,xi[0],16,gi[1],ti[1]]]],[[rwn[li,xi[0],17,gi[0],ti[0]],rwn[li,xi[0],17,gi[0],ti[1]]],[rwn[li,xi[0],17,gi[1],ti[0]],rwn[li,xi[0],17,gi[1],ti[1]]]],[[rwn[li,xi[0],18,gi[0],ti[0]],rwn[li,xi[0],18,gi[0],ti[1]]],[rwn[li,xi[0],18,gi[1],ti[0]],rwn[li,xi[0],18,gi[1],ti[1]]]],[[rwn[li,xi[0],19,gi[0],ti[0]],rwn[li,xi[0],19,gi[0],ti[1]]],[rwn[li,xi[0],19,gi[1],ti[0]],rwn[li,xi[0],19,gi[1],ti[1]]]],[[rwn[li,xi[0],20,gi[0],ti[0]],rwn[li,xi[0],20,gi[0],ti[1]]],[rwn[li,xi[0],20,gi[1],ti[0]],rwn[li,xi[0],20,gi[1],ti[1]]]],[[rwn[li,xi[0],21,gi[0],ti[0]],rwn[li,xi[0],21,gi[0],ti[1]]],[rwn[li,xi[0],21,gi[1],ti[0]],rwn[li,xi[0],21,gi[1],ti[1]]]],[[rwn[li,xi[0],22,gi[0],ti[0]],rwn[li,xi[0],22,gi[0],ti[1]]],[rwn[li,xi[0],22,gi[1],ti[0]],rwn[li,xi[0],22,gi[1],ti[1]]]]],
[[[rwn[li,xi[1],0,gi[0],ti[0]],rwn[li,xi[1],0,gi[0],ti[1]]],[rwn[li,xi[1],0,gi[1],ti[0]],rwn[li,xi[1],0,gi[1],ti[1]]]],[[rwn[li,xi[1],1,gi[0],ti[0]],rwn[li,xi[1],1,gi[0],ti[1]]],[rwn[li,xi[1],1,gi[1],ti[0]],rwn[li,xi[1],1,gi[1],ti[1]]]],[[rwn[li,xi[1],2,gi[0],ti[0]],rwn[li,xi[1],2,gi[0],ti[1]]],[rwn[li,xi[1],2,gi[1],ti[0]],rwn[li,xi[1],2,gi[1],ti[1]]]],[[rwn[li,xi[1],3,gi[0],ti[0]],rwn[li,xi[1],3,gi[0],ti[1]]],[rwn[li,xi[1],3,gi[1],ti[0]],rwn[li,xi[1],3,gi[1],ti[1]]]],[[rwn[li,xi[1],4,gi[0],ti[0]],rwn[li,xi[1],4,gi[0],ti[1]]],[rwn[li,xi[1],4,gi[1],ti[0]],rwn[li,xi[1],4,gi[1],ti[1]]]],[[rwn[li,xi[1],5,gi[0],ti[0]],rwn[li,xi[1],5,gi[0],ti[1]]],[rwn[li,xi[1],5,gi[1],ti[0]],rwn[li,xi[1],5,gi[1],ti[1]]]],[[rwn[li,xi[1],6,gi[0],ti[0]],rwn[li,xi[1],6,gi[0],ti[1]]],[rwn[li,xi[1],6,gi[1],ti[0]],rwn[li,xi[1],6,gi[1],ti[1]]]],[[rwn[li,xi[1],7,gi[0],ti[0]],rwn[li,xi[1],7,gi[0],ti[1]]],[rwn[li,xi[1],7,gi[1],ti[0]],rwn[li,xi[1],7,gi[1],ti[1]]]],[[rwn[li,xi[1],8,gi[0],ti[0]],rwn[li,xi[1],8,gi[0],ti[1]]],[rwn[li,xi[1],8,gi[1],ti[0]],rwn[li,xi[1],8,gi[1],ti[1]]]],[[rwn[li,xi[1],9,gi[0],ti[0]],rwn[li,xi[1],9,gi[0],ti[1]]],[rwn[li,xi[1],9,gi[1],ti[0]],rwn[li,xi[1],9,gi[1],ti[1]]]],[[rwn[li,xi[1],10,gi[0],ti[0]],rwn[li,xi[1],10,gi[0],ti[1]]],[rwn[li,xi[1],10,gi[1],ti[0]],rwn[li,xi[1],10,gi[1],ti[1]]]],[[rwn[li,xi[1],11,gi[0],ti[0]],rwn[li,xi[1],11,gi[0],ti[1]]],[rwn[li,xi[1],11,gi[1],ti[0]],rwn[li,xi[1],11,gi[1],ti[1]]]],[[rwn[li,xi[1],12,gi[0],ti[0]],rwn[li,xi[1],12,gi[0],ti[1]]],[rwn[li,xi[1],12,gi[1],ti[0]],rwn[li,xi[1],12,gi[1],ti[1]]]],[[rwn[li,xi[1],13,gi[0],ti[0]],rwn[li,xi[1],13,gi[0],ti[1]]],[rwn[li,xi[1],13,gi[1],ti[0]],rwn[li,xi[1],13,gi[1],ti[1]]]],[[rwn[li,xi[1],14,gi[0],ti[0]],rwn[li,xi[1],14,gi[0],ti[1]]],[rwn[li,xi[1],14,gi[1],ti[0]],rwn[li,xi[1],14,gi[1],ti[1]]]],[[rwn[li,xi[1],15,gi[0],ti[0]],rwn[li,xi[1],15,gi[0],ti[1]]],[rwn[li,xi[1],15,gi[1],ti[0]],rwn[li,xi[1],15,gi[1],ti[1]]]],[[rwn[li,xi[1],16,gi[0],ti[0]],rwn[li,xi[1],16,gi[0],ti[1]]],[rwn[li,xi[1],16,gi[1],ti[0]],rwn[li,xi[1],16,gi[1],ti[1]]]],[[rwn[li,xi[1],17,gi[0],ti[0]],rwn[li,xi[1],17,gi[0],ti[1]]],[rwn[li,xi[1],17,gi[1],ti[0]],rwn[li,xi[1],17,gi[1],ti[1]]]],[[rwn[li,xi[1],18,gi[0],ti[0]],rwn[li,xi[1],18,gi[0],ti[1]]],[rwn[li,xi[1],18,gi[1],ti[0]],rwn[li,xi[1],18,gi[1],ti[1]]]],[[rwn[li,xi[1],19,gi[0],ti[0]],rwn[li,xi[1],19,gi[0],ti[1]]],[rwn[li,xi[1],19,gi[1],ti[0]],rwn[li,xi[1],19,gi[1],ti[1]]]],[[rwn[li,xi[1],20,gi[0],ti[0]],rwn[li,xi[1],20,gi[0],ti[1]]],[rwn[li,xi[1],20,gi[1],ti[0]],rwn[li,xi[1],20,gi[1],ti[1]]]],[[rwn[li,xi[1],21,gi[0],ti[0]],rwn[li,xi[1],21,gi[0],ti[1]]],[rwn[li,xi[1],21,gi[1],ti[0]],rwn[li,xi[1],21,gi[1],ti[1]]]],[[rwn[li,xi[1],22,gi[0],ti[0]],rwn[li,xi[1],22,gi[0],ti[1]]],[rwn[li,xi[1],22,gi[1],ti[0]],rwn[li,xi[1],22,gi[1],ti[1]]]]]])
	
			nr=len(mg)

			#verificar se entradas sao todas -9
			if np.max(sl)==-9 or np.max(sn)==-9:
				if not silent:
					print ('Model missing from grid or not enough data points')
				al_tot[j_horiz][i_vert]=-9
				an_tot[j_horiz][i_vert]=-9
				co_tot[j_horiz][i_vert]=-9					
				continue
			#remover -9
			dum=0
			for i in range(nr):
				c=np.minimum(sl[:,0,:,:],sn[:,0,:,:])==-9
				if tuple(np.where(c==True)[0])!=():
					if dum >= nr-2:
						if not silent:
							print ('Model missing from grid or not enough data points')
						al_tot[j_horiz][i_vert]=-9
						an_tot[j_horiz][i_vert]=-9
						co_tot[j_horiz][i_vert]=-9
						continue						
					sl=sl[:,1:nr-dum,:,:]
					sn=sn[:,1:nr-dum,:,:]
					mg=mg[1:nr-dum]
					dum=dum+1
				d=np.minimum(sl[:,nr-dum-1,:,:],sn[:,nr-dum-1,:,:])==-9
				if tuple(np.where(d==True)[0])!=():
					if dum >= nr-2:
						if not silent:
							print ('Model missing from grid or not enough data points')
						al_tot[j_horiz][i_vert]=-9
						an_tot[j_horiz][i_vert]=-9
						co_tot[j_horiz][i_vert]=-9
						continue						
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

				al_tot[j_horiz][i_vert]=-9
				an_tot[j_horiz][i_vert]=-9
				co_tot[j_horiz][i_vert]=-9					
				continue
			
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
				al_tot[j_horiz][i_vert]=al
				an_tot[j_horiz][i_vert]=al
				co_tot[j_horiz][i_vert]=co

			else:
				co=an-al
				al_tot[j_horiz][i_vert]=al
				an_tot[j_horiz][i_vert]=an
				co_tot[j_horiz][i_vert]=co
	
	return co_tot


