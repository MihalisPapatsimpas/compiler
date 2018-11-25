outfile2 = None

class Entity:
	def __init__(self, Type, Name, boolean, offset):
		if (Type == "parameter"):
			self.Type = "parameter"
			self.Name = Name
			self.isIn = boolean 
			self.offset = offset
		elif (Type == "function"):
			self.Type = "function"
			self.Name = Name
			self.isFunction = boolean
			self.startQuad = 0
			
			self.argumentList = list()
			self.frameLength = 0
		elif (Type == "variable"):
			self.Type = "variable"
			self.Name = Name
			self.offset = offset
		else:
			print("Invalid Entity constructor")

	def __repr__(self): 
		result = ""
		if self.Type == "function" and self.isFunction == False:
			result = "procedure" + " " + str(self.Name)
		else:
			result = str(self.Type) + " " + str(self.Name)

		if self.Type == "variable":
			result += " off: " + str(self.offset)
		elif self.Type == "function":
			result += str(self.argumentList) + " start: " + str(self.startQuad) + " len: " + str(self.frameLength)
		elif self.Type == "parameter":
			if self.isIn == True:
				result += " in off: " + str(self.offset)
			else:
				result += " inout off: " + str(self.offset)
		return result


class Scope:
	def __init__(self):
		self.offset = 12
		self.entityList = list()

	def addEntity(self, item):
		self.entityList.append(item)
		if item.Type != "function":
			self.offset += 4

	def addArgumentToLast(self, isIn):
		lastEntity = self.entityList[len(self.entityList) - 1]
		lastEntity.argumentList.append(Argument(isIn))


	def __repr__(self): 
		return str(self.entityList)


class Argument:
	def __init__(self, isIn):
		self.isIn = isIn 

	def __repr__(self): 
		if (self.isIn):
			return "in"
		else:
			return "inout"

#list with scopes 
scopeList = list()

def newScope():
	global scopeList
	scopeList.append(Scope())


def deleteScope():
	global scopeList
	outfile2.write("Before deleting scope:\n")
	for i in range(len(scopeList) - 1, -1, -1):
		outfile2.write("Level " + str(i) + ": " + str(scopeList[i]) + "\n")
	outfile2.write("\n")
	scopeList.pop()


def newVariableEntity(name):
	global scopeList
	offset = scopeList[len(scopeList) - 1].offset
	scopeList[len(scopeList) - 1].addEntity(Entity("variable", name, False, offset))


def newFunctionEntity(name, isFunction):
	global scopeList
	scopeList[len(scopeList) - 1].addEntity(Entity("function", name, isFunction, 0))


def newParameterEntity(name, isIn):
	global scopeList
	offset = scopeList[len(scopeList) - 1].offset
	scopeList[len(scopeList) - 1].addEntity(Entity("parameter", name, isIn, offset))


def newArgument(isIn):
	global scopeList
	# find last function in previous scope (pre-last) to add the argument is in or inout
	lastScope = scopeList[len(scopeList) - 2]
	#last argument is the fuction we found 
	lastScope.addArgumentToLast(isIn)


def setLastFunctionStartQuad(startQuad):
	global scopeList
	if len(scopeList) == 1: return # main program
	# find last function in previous scope (pre-last)
	lastScope = scopeList[len(scopeList) - 2]
	lastEntity = lastScope.entityList[len(lastScope.entityList) - 1]
	lastEntity.startQuad = startQuad


def setLastFunctionFrameLength():
	global scopeList
	# find last function in previous scope (pre-last)
	lastScope = scopeList[len(scopeList) - 2]
	currentScope = scopeList[len(scopeList) - 1]
	lastEntity = lastScope.entityList[len(lastScope.entityList) - 1]
	lastEntity.frameLength = currentScope.offset


def findEntity(name):
	global scopeList
	for i in range(len(scopeList) - 1, -1, -1):
		for j in range(0, len(scopeList[i].entityList)):
			if name == scopeList[i].entityList[j].Name:
			    return (scopeList[i].entityList[j], i)
	return None,None


def getCurrentScope():
	global scopeList
	return len(scopeList) - 1


def getMainFrameLength():
	global scopeList
	return scopeList[0].offset


def existsInCurrentScope(name):
	global scopeList
	i = len(scopeList) - 1
	for j in range(0, len(scopeList[i].entityList)):
		if name == scopeList[i].entityList[j].Name:
			return True
	return False


def beginSymbolTableOutput(filename):
	global outfile2
	outfile2 = open(filename, "w")


def endSymbolTableOutput():
	global outfile2
	outfile2.close()
	
