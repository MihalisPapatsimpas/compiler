import string
import sys

text = ""
filename = ""

def textRead(this_filename):
	global text
	global filename

	filename = this_filename
	inputfile = open(this_filename, 'r')
	text = inputfile.readlines()
	inputfile.close()


currentLine = 0
currentColumn = -1

def getNextChar():
	global currentLine
	global currentColumn
	
	currentColumn += 1
	
	if currentColumn >= len(text[currentLine]):
		currentLine += 1
		currentColumn = 0
	if currentLine >= len(text):
		return None     
	
	return (text[currentLine][currentColumn],currentLine + 1,currentColumn + 1)


stage = 0
errorLine = -1
def safeChar():
	global stage
	global currentLine
	charData = getNextChar()
	
	
	if charData == None:                                            #checks if reached eof
		if stage == 0:
			return "EOF"                                    

		if stage == 6:
			print("Syntax error: comments open at line "+ str(errorLine + 1)+ " but never close.")
			exit(None)                                      #it must exit because if i return it will return in lex!

		else:
			print("EOF by safechar()")
			exit(None)                                      #it must exit because if i return it will return in lex!

	c = charData[0]
	return c

def getId(stringtk):
	committedWords = ["program", "endprogram", "declare", "enddeclare", "if", "then", "else", "endif", "while", "endwhile", "repeat", "endrepeat", "exit", "switch", "case", "endswitch", "forcase", "when", "endforcase", "procedure", "endprocedure", "function", "endfunction", "call", "return", "in", "inout", "and", "or", "not", "true", "false", "input", "print"]

	for x in range(0,len(committedWords)):                          #Checks if it is committed word
		if stringtk == committedWords[x]:
			return committedWords[x], committedWords[x]

									#if not commited word is an id                  
	return "Id",stringtk


def goBackOne():
	global currentLine
	global currentColumn
	
	
	if currentColumn == 0:
		return
	else:
		currentColumn -= 1
	return
	
	


endOfFile = False
alphabet = string.ascii_letters + string.digits
symbols = ["+","-","*","/",";",",",":","(",")","[","]","<",">","="]

def lex():
	global currentLine
	global currentColumn
	global stage
	global errorLine

	token = ""
	strg = []
	
	
	while True:

		char = safeChar() 
		if(char == "EOF"):
			return "EOF"
		
		#skips all white charachers
		while stage == 0 and char.isspace():
			char = safeChar()
			if(char == "EOF"):
				return "EOF"
		
		#code for comments
		if stage == 0 and char == "/":
			stage = 6
			errorLine = currentLine
			char = safeChar()
			if(char == "EOF"):
				return "EOF"

			#line comment
			if char == "/":
				currentLine += 1
				currentColumn = -1
				stage = 0
				continue

			#block comment
			if char == "*":
				char = ""
				while True:
					char = safeChar()
					if(char == "EOF"):
						return "EOF"
					if char == "*":
						char = safeChar()
						if(char == "EOF"):
							return "EOF"
						if char == "/":
							stage = 0
							break
						else:
							continue
					else:
						continue
	

			#if not comment then is math operator
			if stage == 6:
				stage = 0
				goBackOne()
				return "mulOperTk","/"
			
				
			

		#not in alphabet
		if char not in alphabet and char not in symbols:
			print("Syntax error: Unknown characher at line " + str(currentLine + 1)+".")
			exit(None)

		#code for strings and commited words
		if stage == 0 and char.isalpha():
			stage = 1
			counter = 0                                     #needed to keep the first 30 digits
			
			while (char.isalpha() or char.isdigit()):
				if counter < 30:                        #saves first 30 characters
					strg.append(char)
				counter += 1
				char = safeChar()
				if(char == "EOF"):
					return "EOF"

			stage = 0
			goBackOne()                                     #goes back one characher
			strg = ''.join(strg)                            #makes it one string
			idData = getId(strg)                            #checks for the token
			token = idData[0]                               #the actual token
			strg = idData[1]                                #the actual string 
			return token,strg

		#code for costants
		if stage == 0 and char.isdigit():
			stage = 2
			
			while char.isdigit():
				strg.append(char)
				char = safeChar()
				if(char == "EOF"):
					return "EOF"
			
			if char.isalpha():
				print("Syntax error: Number cannot be followed by characher at line " + str(currentLine + 1)+".")
				exit(None)
			if char not in symbols and not char.isspace():
				print("Syntax error: Unknown characher at line " + str(currentLine + 1)+".")
				exit(None)
							
			strg = ''.join(strg)                            #makes it one string
			constant = int(strg)                            #casting to number
			

			if constant > 32767:
				print("Constant error: constant out of range at line " + str(currentLine + 1)+".")
				exit(None)
			
			stage = 0
			goBackOne()
			return "constantTk",constant
	
		
		#Code for lesser
		if char == "<":
			stage = 3
			char = safeChar()
			if(char == "EOF"):
				return "EOF"
			if char == "=":
				stage = 0
				return "correlationTk","<="
			elif char == ">":
				stage = 0
				return "correlationTk","<>"
			else:
				stage = 0
				goBackOne()
				return "correlationTk","<"
	
		#Code for greater
		if char == ">":
			stage = 3
			char = safeChar()
			if(char == "EOF"):
				return "EOF"
			
			if char == "=":
				stage = 0
				return "correlationTk",">="
			else:
				stage = 0
				goBackOne()
				return "correlationTk",">"
		
		#Code for := or :
		if char == ":":
			stage = 5
			char = safeChar()
			if(char == "EOF"):
				return "EOF"
			
			if char == "=":
				stage = 0
				return "inputTk",":="
			else:
				stage = 0
				goBackOne()
				return "upDownTk",":"
		
		#Code for seperators exept : i return it at :=
		if char == ";":
			return "semiColumnTk",";"
		if char == ",":
			return "commaTk",","

		#Code for math parenthesis
		if char == "(":
			return "leftparenthesisTk","("
		if char == ")":
			return "rightparenthesisTk",")"
		
		#Code for logical parenthesis
		if char == "[":
			return "leftlogicparenthesisTk","["
		if char == "]":
			return "rightlogicparenthesisTk","]"
		
		#Code for math operators exept / i return it at comments
		if char == "+" or char == "-":
			return "addOperTk",char
		
		if char == "*":
			return "mulOperTk",char

		if char == "=":
			   return "equalTk",char

def getLineAndColumn():
	global currentLine
	global currentColumn

	return  currentLine, currentColumn
