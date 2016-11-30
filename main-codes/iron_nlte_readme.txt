#
#FUNCTION iron_nlte:
#
#	it allows the calculation of LTE/NLTE abundances for a given neutral iron EW, using linear interpolation
#
#	IMPORTANT: You must have the grid given by Karin, wich is "iron_grid.sav". You should change its directory path!!!
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

