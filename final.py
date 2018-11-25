def gnvlcode(v):
	entity, i = findEntity(v)
	outPutFinalCode("lw $t0, -4($sp)")
	for j in range(getCurrentScope() - i):
		outPutFinalCode("lw $t0, -4($t0)")
	outPutFinalCode("add $t0, $t0, -" + str(entity.offset))


def loadvr(v, r):
	entity, i = findEntity(v)
	if entity == None: # constant value
		outPutFinalCode("li $t" + str(r) + ", " + str(v))
		return
	scope_depth = getCurrentScope() - i
	if i == 0: # global variable
		outPutFinalCode("lw $t" + str(r) + ", -" + str(entity.offset) + "($s0)")
	elif scope_depth == 0 and ((entity.Type == "variable") or (entity.Type == "parameter" and entity.isIn == True)):
		outPutFinalCode("lw $t" + str(r) + ", -" + str(entity.offset) + "($sp)")
	elif entity.Type == "parameter" and entity.isIn == False and scope_depth == 0:
		outPutFinalCode("lw $t0, -" + str(entity.offset) + "($sp)")
		outPutFinalCode("lw $t" + str(r) + ", ($t0)")
	elif scope_depth != 0 and (entity.Type == "variable" or
            (entity.Type == "parameter" and entity.isIn == True)):
		gnvlcode(v)
		outPutFinalCode("lw $t" + str(r) + ", ($t0)")
	elif scope_depth != 0 and (entity.Type == "variable" or
            (entity.Type == "parameter" and entity.isIn == False)):
		gnvlcode(v)
		outPutFinalCode("lw $t0, ($t0)")
		outPutFinalCode("lw $t" + str(r) + ", ($t0)")
	else:
		print("ERROR")

def storerv(r, v):
	entity, i = findEntity(v)
	scope_depth = getCurrentScope() - i
	if i == 0: # global variable
		outPutFinalCode("sw $t" + str(r) + ", -" + str(entity.offset) + "($s0)")
	elif scope_depth == 0 and ((entity.Type == "variable") or (entity.Type == "parameter" and entity.isIn == True)):
		outPutFinalCode("sw $t" + str(r) + ", -" + str(entity.offset) + "($sp)")
	elif entity.Type == "parameter" and entity.isIn == False and scope_depth == 0:
		outPutFinalCode("lw $t0, -" + str(entity.offset) + "($sp)")
		outPutFinalCode("sw $t" + str(r) + ", ($t0)")
	elif scope_depth != 0 and (entity.Type == "variable" or
            (entity.Type == "parameter" and entity.isIn == True)):
		gnvlcode(v)
		outPutFinalCode("sw $t" + str(r) + ", ($t0)")
	elif scope_depth != 0 and (entity.Type == "variable" or
            (entity.Type == "parameter" and entity.isIn == False)):
		gnvlcode(v)
		outPutFinalCode("lw $t0, ($t0)")
		outPutFinalCode("sw $t" + str(r) + ", ($t0)")
	else:
		print("ERROR")


startQuadIndex = 0
def genFinalCode():
	global startQuadIndex
	global quads
	nextParameter = 0
	currentFunction = ""
   
	for i in range(startQuadIndex, nextQuad()):
		outPutFinalCode("L" + str(i) + ":")
		current = quads[i]
		if (current[0] == "jump"):
			outPutFinalCode("j L" + str(current[3]))
		elif current[0] in ["<", ">", "<=", ">=", "=", "<>"]:
			loadvr(current[1], 1)
			loadvr(current[2], 2)
			outPutFinalCode(getBranch(current[0]) + ", $t1, $t2, L" + str(current[3]))
		elif current[0] == ":=":
			loadvr(current[1], 1)
			storerv(1, str(current[3]))
		elif current[0] in "+-*/":
			loadvr(current[1], 1)
			loadvr(current[2], 2)
			outPutFinalCode(getOperator(current[0]) + " $t1, $t1, $t2")
			storerv(1, str(current[3]))
		elif current[0] == "out":
			outPutFinalCode("li $v0, 1")
			loadvr(current[1], 1)
			outPutFinalCode("add $a0, $t1, 0")
			outPutFinalCode("syscall")
			outPutFinalCode("addi $a0, $0, 0xA") # To print a newline
			outPutFinalCode("addi $v0, $0, 0xB")
			outPutFinalCode("syscall")
		elif current[0] == "inp":
			outPutFinalCode("li $v0, 5")
			outPutFinalCode("syscall")
			outPutFinalCode("move $t1, $v0")
			storerv(1, str(current[1]))
		elif current[0] == "RET":
			loadvr(current[1], 1)
			outPutFinalCode("lw $t0, -8($sp)")
			outPutFinalCode("sw $t1, ($t0)")
			outPutFinalCode("lw $ra, ($sp)")
			outPutFinalCode("jr $ra")
		elif current[0] == "begin_block":
			currentFunction = current[1]
			if current[1] == "__main":
				outPutFinalCode("__main:")
				outPutFinalCode("add $sp, $sp, " + str(getMainFrameLength()))
				outPutFinalCode("move $s0, $sp")
			else:
				outPutFinalCode("sw $ra, ($sp)")
		elif current[0] == "end_block":
			if current[1] != "__main": # main function does not return
				outPutFinalCode("lw $ra, ($sp)")
				outPutFinalCode("jr $ra")
		elif current[0] == "par":
			if nextParameter == 0:
				outPutFinalCode("add $fp, $sp, ?")
			if current[2] == "CV":
				loadvr(current[1], 0)
				outPutFinalCode("sw $t0, -" + str(12+4*nextParameter) + "($fp)")
		elif current[2] == "REF":
			writeRefParameter(current[1], nextParameter)
		elif current[2] == "RET":
			entity, _ = findEntity(current[1])
			outPutFinalCode("add $t0, $sp, -" + str(entity.offset))
			outPutFinalCode("sw $t0, -8($fp)")
			nextParameter += 1
		elif current[0] == "call":
			f, fScope = findEntity(current[1])
			if currentFunction == "__main":
				frameLength = getMainFrameLength()
				cScope = -1
			else:
				c, cScope = findEntity(currentFunction)
				frameLength = c.frameLength
			if fScope == cScope:
				outPutFinalCode("lw $t0, -4($sp)")
				outPutFinalCode("sw $t0, -4($fp)")
			else:
				outPutFinalCode("sw $sp, -4($fp)")
			replaceUnknownLength(f.frameLength)
			outPutFinalCode("add $sp, $sp, " + str(f.frameLength))
			outPutFinalCode("jal L" + str(f.startQuad))
			outPutFinalCode("add $sp, $sp, -" + str(f.frameLength))
			nextParameter = 0
		elif current[0] != "halt":
			print("Unknown command: " + current[0])
	startQuadIndex = nextQuad()
	flushFinalCode()

def writeRefParameter(parameter, parameterID):
	entity, i = findEntity(parameter)
	scope_depth = getCurrentScope() - i
	if scope_depth == 0 and ((entity.Type == "variable") or (entity.Type == "parameter" and entity.isIn == True)):
		outPutFinalCode("add $t0, $sp, -" + str(entity.offset))
		outPutFinalCode("sw $t0, -" + str(12+4*parameterID) + "($fp)")
	elif entity.Type == "parameter" and entity.isIn == False and scope_depth == 0:
		outPutFinalCode("lw $t0, -" + str(entity.offset) + "($sp)")
		outPutFinalCode("sw $t0, -" + str(12+4*parameterID) + "($fp)")
	elif scope_depth != 0 and (entity.Type == "variable" or
            (entity.Type == "parameter" and entity.isIn == True)):
		gnvlcode(parameter)
		outPutFinalCode("sw $t0, -" + str(12+4*parameterID) + "($fp)")
	elif scope_depth != 0 and (entity.itemType == "variable" or
            (entity.Type == "parameter" and entity.isIn == False)):
		gnvlcode(parameter)
		outPutFinalCode("lw $t0, ($t0)")
		outPutFinalCode("sw $t0, -" + str(12+4*parameterID) + "($fp)")
	else:
		print("ERROR")

def getOperator(op):
	if op == "+": return "add"
	elif op == "-": return "sub"
	elif op == "*": return "mul"
	else: return "div"

def getBranch(relop):
	if relop == "<": return "blt"
	elif relop == ">": return "bgt"
	elif relop == "<=": return "ble"
	elif relop == ">=": return "bge"
	elif relop == "=": return "beq"
	else: return "bne"

outfile = None
def beginFinalCodeOutput(filename):
	global outfile
	outfile = open(filename, "w")
	outPutFinalCode("j __main")


def endFinalCodeOutput():
	global outfile
	outfile.close()


outBuffer = ""
def outPutFinalCode(line):
	global outBuffer
	outBuffer += line + "\n"


def replaceUnknownLength(length):
	global outBuffer
	outBuffer = outBuffer.replace("?", str(length))


def flushFinalCode():
	global outfile
	global outBuffer
	outfile.write(outBuffer)
	outBuffer = ""
