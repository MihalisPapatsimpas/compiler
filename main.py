import sys
import os
import lexi
import syntax
import intermediate
import symbolTable
import final

def main():	
	arg = "Input file"
	newArg = arg.split('.')
	if newArg[1] == "ci":
		symbolTable.beginSymbolTableOutput("./" + newArg[0] + ".symbolTable")
		final.beginFinalCodeOutput("./" + newArg[0] + ".asm")
		lexi.textRead(arg)
		syntax.program()
		intermediate.outputIntermediateCode("./" + newArg[0] + ".int")
		intermediate.outputEquivalentCCode("./" + newArg[0] + ".c")
		symbol.endSymbolTableOutput()
		symbol.endFinalCodeOutput()
	else:
		print("Wrong file format. File must end with .ci")
				
if __name__ == '__main__':
   main()
