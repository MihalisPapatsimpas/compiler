import sys
import os

import lexi
import intermediate
import symbolTable
import final

def program():
		global token 
		token = lexi.lex()
		if token[0] == "program":
				token = lexi.lex()
				if token[0] == "Id":
						symbolTable.newScope()
						programId = "__main"
						token = lexi.lex()
						block(programId)
						symbolTable.setLastFunctionFrameLength()
						if token[0] == "endprogram":
								final.genQuad("halt", "_", "_", "_")
								intermediate.genQuad("end_block", programId, "_", "_")
								final.genFinalCode()
								symbolTable.deleteScope()
								token = lexi.lex()
								if token == "EOF":
										print("Passed Test Successfully!")
								else:
										line = lexi.getLineAndColumn()
										print("Syntax error: code after 'endprogram' statement at line " + str(line[0] + 1)+".")
										exit()
						else:
								print("Syntax error: 'endprogram' statement is missing.")
								exit()
				else:
						print("Syntax error: program name is missing at line.")
						exit()
		else:
				print("Syntax error: 'program' statement is missing.")
				exit()


def block(blockId = None):
		declarations()
		subprograms()
		if blockId != None:
			symbolTable.setLastFunctionStartQuad(nextQuad())
			intermediate.genQuad("begin_block", blockId, "_", "_")

		statements()


def declarations():
		global token
		if token[0] == "declare":
				token = lexi.lex()
				varlist()
		else:
				return


def varlist():
		global token
		if token[0] == "Id":
				checkAlreadyDeclaredIdentifier()
				symbolTable.newVariableEntity(token[1])
				lexi.token = lex()
				while token[0] != "enddeclare":
						if token[0] == "commaTk":
								token = lexi.lex()
								checkAlreadyDeclaredIdentifier()
								symbolTable.newVariableEntity(token[1])
								if token[0] == "Id":
										token = lexi.lex()
								else:
										line = lexi.getLineAndColumn()
										print("Syntax error: Invalid arguments after ',' at line " + str(line[0] + 1)+".")
										exit()
						else:
								line = lexi.getLineAndColumn()
								print("Syntax error: Invalid arguments at 'declare' statement at line " + str(line[0] + 1)+".")
								exit()

				token = lexi.lex()
				return
		elif token[0] == "enddeclare":
				token = lexi.lex()
				return
		else:
				line = lexi.getLineAndColumn()
				print("Syntax error: 'enddeclare' is missing at line " + str(line[0] + 1)+".")
				exit()




def subprograms():
		global token
		procorfunc()
		while token[0] == "procedure" or token[0] == "function":
				procorfunc()
		return


funcList = list()
def procorfunc():
		global token
		global funcList
		global inFunction
		global returnFound 

		returnFound = False
		token2 = ""
		if token[0] == "procedure" or token[0] == "function":
				token2 = token[0]
				token = lexi.lex()
				if token[0] == "Id":
						checkAlreadyDeclaredIdentifier()
						inFunctionLocal = inFunction
						inFunction = False
						if token2 == "function":
							inFunction = True
							symbolTable.newFunctionEntity(token[1], True)
							symbolTable.newScope()
						else:
							symbolTable.newFunctionEntity(token[1], False)
							symbolTable.newScope()
						name = token[1]
						funcList.append(name)
						token = lexi.lex()
						procorfuncbody(token2, name)
						if token2 == "procedure":
								if token[0] == "endprocedure":
										final.genFinalCode()
										symbolTable.deleteScope()
										token = lexi.lex()
										return
								else:
										print("Syntax error: 'endprocedure' statement expected.")
										exit()
						elif token2 == "function":
								if token[0] == "endfunction":
										final.genFinalCode()
										symbolTable.deleteScope()
										token = lexi.lex()
										if returnFound == False and inFunction == True:
											print("No 'return' statement found in function.")
											returnFound = False
											inFunction = inFunctionLocal
											exit()
										return
								else:
										print("Syntax error: 'endfunction' statement expected.")
										exit()
								
				else:
						line = lexi.getLineAndColumn()
						print("Syntax error: '"+str(token2)+"' name is missing at line " + str(line[0] + 1)+".")
						exit()





def procorfuncbody(typeOfToken, functionName):
		formalpars()
		block(functionName)
		symbolTable.setLastFunctionFrameLength()
		intermediate.genQuad("end_block", functionName, "_", "_")
		return



def formalpars():
		global token 
		if token[0] == "leftparenthesisTk" :
				token = lexi.lex()
				formalparlist()
		else:
				line = lexi.getLineAndColumn()
				print("Syntax error: '(' statement is missing at line " + str(line[0]+1)+".") 
		return 


def formalparlist():
		global token 
		while token[0] != "rightparenthesisTk":
				formalparitem()
				if token[0] == "commaTk" :
						token = lexi.lex()
						formalparitem() 
						if token[0] != "rightparenthesisTk":
								token = lexi.lex()           
		token = lex()
		return



def formalparitem():
		global token

		if token[0] == "inout" or token[0] == "in":
			isIn = False
			if token[0] == "in": isIn = True

			token = lex()
			symbolTable.newArgument(isIn)
			symbolTable.newParameterEntity(token[1], isIn)
			if token[0] != "Id" :           
					line = lexi.getLineAndColumn()
					print("Syntax error: 'Parameter' is missing at line " + str(line[0]+1)+".") 
					exit()
			else:
					token = lexi.lex()
						
					return
		else:
			line = lexi.getLineAndColumn()
			print("Syntax error: 'inout' or 'in' statement is missing at line " + str(line[0]+1)+".") 
			exit()

def statements():
		global token
		statement()
		while token[0] == "semiColumnTk":
				token = lexi.lex()
				statement()
		return

exitList = intermediate.emptyList()
var = ""
exitFound = False
inRepeat = False
returnFound = False
inFunction = False
def statement():
		global token 
		global exitList
		global var
		if token[0] == "Id":
				checkUndeclaredIdentifier()
				var = token[1]
				token = lexi.lex()
				if token[0] == "inputTk":
						token = lexi.lex()
						assignmentStat(var)
				else:
						line = lexi.getLineAndColumn()
						print("Syntax error: expected ':=' statement after variable at line " + str(line[0]+1)+".") 
						exit()

		elif token[0] == "repeat":
				token = lexi.lex()
				repeatStat()

		elif token[0] == "if":
				token = lexi.lex()
				ifStat()
		
		elif token[0] == "while":
				token = lexi.lex()
				whileStat()
		
		elif token[0] == "exit":
				exitFound = True
				if inRepeat == False:
					print("'exit' statement found outside of repeat.")
					exit()
				bExit = intermediate.makeList(nextQuad())    
				genQuad("jump", "_", "_", "_")
				exitList = intermediate.merge(exitList, bExit)           #list with jumps potition 
				token = lexi.lex()

		elif token[0] == "switch":
				token = lexi.lex()
				switchStat()
		
		elif token[0] == "forcase":
				token = lexi.lex()
				forcaseStat()

		elif token[0] == "call":
				token = lexi.lex()
				callId = token[1]
				callStat(callId)
		
		elif token[0] == "return":
				returnFound = True
				if inFunction == False:
					print("'return' statement found outside of function.")
					exit()
				token = lexi.lex()
				returnStat()
		
		elif token[0] == "input":
				token = lexi.lex()
				inputStat()
		
		elif token[0] == "print":
				token = lexi.lex()
				printStat()
		
		else:
				return

		return

def printStat():
		global token
		e = expression()
		intermediate.genQuad("out", e, "_", "_")
		return


def inputStat():
		global token
		if token[0] == "Id":
				idToken = token[1]
				intermediate.genQuad("inp", idToken, "_", "_")
				token = lexi.lex()
				return
		else:
				line = lexi.getLineAndColumn()
				print("Syntax error: input is missing at line " + str(line[0]+1)+".") 
				exit()




def forcaseStat():
		global token
		flag = intermediate.newTemp()
		forQuad = intermediate.nextQuad()
		intermediate.genQuad(":=", "0", "_", flag)
		while token[0] != "endforcase":
				if token[0] == "when":
						token = lexi.lex()
						(bTrue, bFalse) = condition()
						intermediate.backPatch(bTrue, intermediate.nextQuad())
						if token[0] == "upDownTk":
								token = lexi.lex()
								statements()
								genQuad(":=", "1", "_", flag)
								intermediate.backPatch(bFalse, intermediate.nextQuad())
						else:
								line = lexi.getLineAndColumn()
								print("Syntax error: expected ':' at line " + str(line[0]+1)+".") 
								exit()
				else:
						line = lexi.getLineAndColumn()
						print("Syntax error: expected 'when' at line " + str(line[0]+1)+".") 
						exit()
								
		intermediate.genQuad("=", flag, "1", forQuad)
		token = lexi.lex()
		return


def switchStat():
		global token
		exitList = intermediate.emptyList()
		e1 = expression()
		while token[0] != "endswitch": 
				if token[0] == "case":
						token = lexi.lex()
						e2 = expression()
						if token[0] == "upDownTk":

								bTrue = intermediate.makeList(intermediate.nextQuad())    #references ["=", e1, e2, "_"]
								intermediate.genQuad("=", e1, e2, "_")
								bFalse = intermediate.makeList(intermediate.nextQuad())   #references ["jump", "_", "_", "_"]
								intermediate.genQuad("jump", "_", "_", "_")
								intermediate.backPatch(bTrue, intermediate.nextQuad())    # ["=", e1, e2, tells where to go]

								token = lexi.lex()
								statements()

								tList = intermediate.makeList(intermediate.nextQuad())
								intermediate.genQuad("jump", "_", "_", "_")
								exitList = intermediate.merge(exitList, tList)
								intermediate.backPatch(bFalse, intermediate.nextQuad())
						else:
								line = getLineAndColumn()
								print("Syntax error: expected ':' at line " + str(line[0]+1)+".") 
								exit()
				else:
						line = lexi.getLineAndColumn()
						print("Syntax error: 'endswitch' or 'case' statement is missing .") 
						exit()

		intermediate.backPatch(exitList, intermediate.nextQuad())
		token = lexi.lex()
		return


def whileStat():
		global token
		q = intermediate.nextQuad()
		(bTrue, bFalse) = condition()
		intermediate.backPatch(bTrue, intermediate.nextQuad())
		statements()
		intermediate.genQuad("jump","_","_", q)
		intermediate.backPatch(bFalse,nextQuad())
		if token[0] == "endwhile":
				token = lexi.lex()
				return
		else:
				print("Syntax error: 'endwhile' statement is missing. " ) 
				exit()

def ifStat():   
		global token
		(bTrue, bFalse) = condition()
		if token[0] == "then":
				
				intermediate.backPatch(bTrue, intermediate.nextQuad())
				token = lexi.lex()
				statements()
				ifList = intermediate.makeList(intermediate.nextQuad())
				intermediate.genQuad("jump","_","_","_")
				intermediate.backPatch(bFalse, intermediate.nextQuad())
				elsepart()
				intermediate.backPatch(ifList, intermediate.nextQuad())
				if token[0] == "endif":
						token = lexi.lex()
						return
				else:
						print("Syntax error: 'endif' statement is missing.") 
						exit()
		else:
				line = lexi.getLineAndColumn()
				print("Syntax error: 'then' statement is missing at line " + str(line[0]+1)+".") 
				exit()

def elsepart():
		global token
		if token[0] == "else":
				token = lexi.lex()
				statements()
				return
		return



def condition():
		global token
		(q1True, q1False) = boolterm()
		bTrue = q1True
		bFalse = q1False
		while token[0] == "or":
				token = lexi.lex()
				intermediate.backPatch(bFalse, intermediate.nextQuad())
				(q2True, q2False) = boolterm()
				bTrue = intermediate.merge(bTrue, q2True)
				bFalse = q2False
		return (bTrue, bFalse)
 

def boolterm():
		global token
		(r1True, r1False) = boolfactor()
		qTrue = r1True
		qFalse = r1False
		while token[0] == "and":
				token = lexi.lex()
				intermediate.backPatch(qTrue, nextQuad())
				(r2True, r2False) = boolfactor()
				qFalse = intermediate.merge(qFalse, r2False)
				qTrue = r2True
		return (qTrue, qFalse)

def boolfactor():
		global token
		if token[0] == "not":
				token = lexi.lex()
				if token[0] == "leftlogicparenthesisTk":
						token = lexi.lex()
						(q1True, q1False) = condition()
						if token[0] != "rightlogicparenthesisTk":
								line = lexi.getLineAndColumn()
								print("Syntax error: ']' statement is missing at line " + str(line[0]+1)+".") 
								exit()

						token = lexi.lex()
						return (q1False,q1True)
				else:
						line = lexi.getLineAndColumn()
						print("Syntax error: '[' statement is missing at line " + str(line[0]+1)+".") 
						exit()

		elif token[0] == "leftlogicparenthesisTk":
				token = lexi.lex()
				(q1True, q1False) = condition()
				if token[0] != "rightlogicparenthesisTk":
						line = lexi.getLineAndColumn()
						print("Syntax error: ']' statement is missing at line " + str(line[0]+1)+".") 
						exit()
				token = lexi.lex()
				return (q1True, q1False)
		elif token[0] == "true" or token[0] == "false":
				if token[0] =="true":
						q2True = intermediate.makeList(intermediate.nextQuad())
						q2False = intermediate.emptyList()
						intermediate.genQuad("true", "_", "_", "_")
				else:
						q2False = intermediate.makeList(intermediate.nextQuad())
						q2True = intermediate.emptyList()
						intermediate.genQuad("false", "_", "_", "_")
				token = lexi.lex()
				return (q2True, q2False)
		else:
				expression1 = expression()
				relop = relationalOper()
				expression2 = expression()
				rTrue = makeList(intermediate.nextQuad())
				intermediate.genQuad(relop, expression1, expression2, "_")
				rFalse = makeList(intermediate.nextQuad())
				intermediate.genQuad("jump", "_", "_", "_")
				return (rTrue, rFalse)

def relationalOper():
		global token
		relationalList = ["=","<=",">=",">","<","<>"]
		x = token[1]
		relopType = token[1]                    #return operator
		for x in range(0,len(relationalList)):
				token = lexi.lex()
				return relopType
		else:
				line = lexi.getLineAndColumn()
				print("Syntax error: 'relational operator' is missing at line " + str(line[0]+1)+".") 
				exit()


def repeatStat():
		global token
		global exitList
		global inRepeat
		currentExitList = exitList              #temp list with all the values
		exitList = intermediate.emptyList()                  #clear the global exitList
		inRepeat = True
		bRepeat = intermediate.nextQuad()                    #beginning of repeat
		while token[0] != "endrepeat":
				statements()
		inRepeat = False
		genQuad("jump", "_", "_", bRepeat)      #jump to the start of repeat
		outOfRepeat = intermediate.nextQuad()                #out of the repeat
		backPatch(exitList, outOfRepeat)        #backPatch the current out of repeat
		exitList = currentExitList              #give back to global list
		token = lexi.lex()
		return


def assignmentStat(var):
		expr = expression()
		if expr != None: 
			intermediate.genQuad(":=", expr, "_", var)
		return
 

def expression():
		global token
		optionalSign()
		t1 = term()                             #first term of expression
		while token[0] == "addOperTk":
				tokenOper = token[1]    #operator (+ or -)
				addOper()
				t2 = term()             #second term of expression
				w = intermediate.newTemp()
				intermediate.genQuad(tokenOper,t1,t2,w)
				t1 = w
				
		return t1

def addOper():
		global token
		token = lexi.lex()
		return

def mulOper():
		global token
		token = lexi.lex()
		return

def optionalSign():
		global token
		if token[0] == "addOperTk":
				token = lexi.lex()
				return

		return

def term():
		global token
		f1 = factor()                           #first term of factor
		while token[0] == "mulOperTk":
				tokenOper = token[1]    #operator (* or /)
				mulOper()               #moves lex to next token
				f2 = factor()           #second term of factor
				w = intermediate.newTemp()           # new variable
				intermediate.quads.append([tokenOper, f1, f2, w])    
				f1 = w                  #the total sum to this point
		return f1
	
def idTail(identifier):
		global var
		global token
		global funcList
		
		functionItem, _ = symbolTable.findEntity(identifier) 
		a = actualPars(identifier, functionItem)
		if identifier in funcList:
			current_Temp = intermediate.newTemp()
			intermediate.genQuad("par",current_Temp,"RET","_")
			intermediate.genQuad("call",identifier,"_","_")
			intermediate.genQuad(":=",current_Temp,"_",var)
			
		return a

def returnStat():
		global token
		returnValue = expression()
		genQuad("RET", returnValue, "_", "_")
		return returnValue

def factor():
		global token

		if token[0] == "constantTk" :
				constant = token[1]
				token = lexi.lex()
				return constant
		elif token[0] == "Id":
				checkUndeclaredIdentifier()
				identifier = token[1]
				token = lexi.lex()
				return idTail(identifier)
		elif token[0] =="leftparenthesisTk":
				token = lex()
				expression1 = expression()
				if token[0] == "rightparenthesisTk" :
						token = lexi.lex()
						return expression1
				else:
						line = lexi.getLineAndColumn()
						print("Syntax error: ')' is missing at line " + str(line[0]+1)+".") 
						exit()
		else:
				line = lexi.getLineAndColumn()
				print("Syntax error: 'actualParameter' is missing at line " + str(line[0]+1)+".") 
				exit()


a = ""
counter  = 0
param = list()
def callStat(callId):
	
		global token
		global a
		global param
		global counter
		global temp
	
		if counter == 0:
			a = intermediate.newTemp()
			param.append(a)
			counter += 1
		if token[0] == "Id":
				functionItem, _ = symbolTable.findEntity(token[1])
				procedureName = token[1]
				token = lexi.lex()
				actualPars(procedureName, functionItem) 	
				
				if token[0] == "rightparenthesisTk" or token[0]== "commaTk":		
					
					intermediate.genQuad("par", temp, "RET", "_")
					intermediate.genQuad("call", callId, "_", "_")
				else:
					for i in  range(1,len(param)):
						intermediate.genQuad("par",param[i],"in","_")
					intermediate.genQuad("par",param[0],"RET","_")
					intermediate.genQuad("call", callId, "_", "_")
					counter = 0
					param = []
						
		else:
				line = lexi.getLineAndColumn()
				print("Syntax error: 'function' name is missing at line " + str(line[0]+1)+".") 
				exit()


def actualPars(identifier, functionItem):
		global token
		if token[0] == "leftparenthesisTk" :
				token = lexi.lex()
				actualParlist(functionItem)
				if token[0] == "rightparenthesisTk":
						token = lexi.lex()
						return

				else:
						line = lexi.getLineAndColumn()
						print("Syntax error: ')' is missing at line " + str(line[0]+1)+".") 
						exit()                        
		else:
				return identifier

temp = ""
def actualParlist(functionItem):
		global token
		global counter
		global param
		argumentId = 0
		actualParitem(functionItem, argumentId)
		while token[0] == "commaTk":
				argumentId += 1
				token = lexi.lex()
				actualParitem(functionItem, argumentId)   
	   
		return

def actualParitem(functionItem, argumentId):
	global token
	global param
	global counter
	global temp
	if token[0] == "in":
		if functionItem.argumentList[argumentId].isIn == False:
			print("Expected 'inout' but found 'in'")
			exit()
		token = lexi.lex()
		actualParId = token[1]
		exp = expression()
		intermediate.genQuad("par", exp, "CV", "_")
		return
	elif token[0] == "inout":
		if functionItem.argumentList[argumentId].isIn == True:
			print("Expected 'in' but found 'inout'")
			exit()
		token = lexi.lex()
		if token[0] == "Id":
			checkUndeclaredIdentifier()
			actualParId = token[1]
			intermediate.genQuad("par", actualParId, "REF", "_")
			token = lexi.lex()
			return
		else:
			line = lexi.getLineAndColumn()
			print("Syntax error: 'Parameter' is missing at line " + str(line[0]+1)+".") 
			exit()
	elif token[0] == "call":
		temp = intermediate.newTemp()
		param.append(temp)
		counter += 1
		token = lexi.lex()
		callId = token[1]
		callStat(callId)
	else:
		line = lexi.getLineAndColumn()
		print("Syntax error: 'in' or 'inout' is missing at line " + str(line[0] + 1) +".") 
		exit()

def checkUndeclaredIdentifier():
	global token
	identifier, _  = symbolTable.findEntity(token[1])
	if identifier == None:
		print("Identifier '" + token[1] + "' is not declared for current scope.")
		exit()


def checkAlreadyDeclaredIdentifier():
	global token
	if symbolTable.existsInCurrentScope(token[1]):
		print("Identifier '" + token[1] + "' is already declared for current scope.")
		exit()

