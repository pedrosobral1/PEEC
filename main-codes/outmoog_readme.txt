#FUNCTION outmoog:
#
#	it uses iron_nlte and readoutmoog functions to calculate NLTE abundances for some iron lines. These lines are given by an input file (obtained using MOOG method).
#
#	IMPORTANT: You must have the grid given by Karin, wich is "iron_grid.sav". You should change its directory path!!!
#
#INPUTS:
#
#	dir_input	directory of the input MOOG file (str)
#	name_input	name of the input MOOG file to read (str)
#	dir_output	directory for the output file (str)
#	name_output	name of the output txt files (str)
#	rem		removes (1) or keeps (0) the null nlte values. If 0 is chosen, it calculates the average NLTE abundance for those null points.
#
#
#OUTPUTS:
#
#	3 txt files (lte, nlte abundances and lines with null nlte values) <=> ("name_output_lte.txt","name_output_nlte.txt","name_output_null_nlte.txt")
#
#
#
#
#
#CALLING EXAMPLE:
#
#	outmoog("/home/pedrosobral/PEEC","output","/home/pedrosobral/results","mine",1)
#
#	This uses the "/home/pedrosobral/PEEC/output.moog" file and exports the outputs to "/home/pedrosobral/results"
#


