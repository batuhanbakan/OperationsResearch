import numpy as np

class Simplex:
    
    def __init__(self, obj, lhs, rhs, dir, opt):
        
        self.obj = obj
        self.lhs = lhs
        self.rhs = rhs
        self.dir = dir
        self.opt = opt

        self.objValue = 0.0

        self.isStandard = False
        self.isOptimized = False

        self.varNames = []
        self.slackVarIndices = []
        self.surplusVarIndices = []
        self.artificialVarIndices = []
        self.basicVarIndices = []
        
        self.biggestValue = self.updateBiggestValue()
        
    def setVarNames(self):
        
        for i in range(len(self.obj)):
            self.varNames.append(f"X{i+1}")

    def mFix(self):
        
        self.row, self.col = self.lhs.shape
        
        for i in range(len(self.lhs)):
            self.bi = self.basicVarIndices[i]
            
            if self.bi in self.artificialVarIndices:
                
                if self.opt == "MAX":
                    self.obj = self.obj + (self.biggestValue * self.lhs[i, :])
                    self.objValue = self.objValue - (self.biggestValue * self.rhs[i])
                    
                else:
                    self.obj = self.obj - (self.biggestValue * self.lhs[i, :])
                    self.objValue = self.objValue + (self.biggestValue * self.rhs[i])
        
    def updateBiggestValue(self):
        
        self.big = np.array([])
            
        if np.any(self.lhs):
            self.big = np.append(self.big, self.lhs.max())
            
        if np.any(self.rhs):
            self.big = np.append(self.big, self.rhs.max())
            
        if np.any(self.obj):
            self.big = np.append(self.big, self.obj.max())
            
        return self.big.max() * 10


    def invert(self, d):

        self.d = d

        if self.d == "LE":
            return "GE"

        elif self.d == "GE":
            return "LE"

        else:
            return "EQ"


    def addSlackVar(self, constraintIndex):

        self.constraintIndex = constraintIndex
        
        self.row, self.col = self.lhs.shape
        self.zs = np.zeros((self.row, 1))

        self.lhs = np.concatenate((self.lhs, self.zs), axis = 1)
        self.lhs[self.constraintIndex][self.col] = 1

        self.obj = np.append(self.obj, 0.0)
        
        self.slackVarIndices.append(self.col)
        self.basicVarIndices.append(self.col)

        self.dir[self.constraintIndex] = "EQ"
        


    def addSurplusVar(self, constraintIndex):

        self.constraintIndex = constraintIndex
        
        self.row, self.col = self.lhs.shape
        self.zs = np.zeros((self.row, 1))

        self.lhs = np.concatenate((self.lhs, self.zs), axis = 1)
        self.lhs[self.constraintIndex][self.col] = -1

        self.obj = np.append(self.obj, 0.0)
        
        self.surplusVarIndices.append(self.col)

        self.dir[self.constraintIndex] = "EQ"


    def addArtificialVar(self, constraintIndex):
        
        self.constraintIndex = constraintIndex
        
        self.row, self.col = self.lhs.shape
        self.zs = np.zeros((self.row, 1))

        self.lhs = np.concatenate((self.lhs, self.zs), axis = 1)
        self.lhs[self.constraintIndex][self.col] = 1
        

        if self.opt == "MAX":
            self.obj = np.append(self.obj, -self.biggestValue)
        
        else:
            self.obj = np.append(self.obj, self.biggestValue)

            
        self.artificialVarIndices.append(self.col)
        self.basicVarIndices.append(self.col)

        self.dir[self.constraintIndex] = "EQ"


    def makeRhsPositive(self):

        for i in range(len(self.rhs)):
            
            if self.rhs[i] < 0:
                
                self.lhs[i] = -self.lhs[i]
                self.rhs[i] = -self.rhs[i]

                self.dir[i] = self.invert(self.dir[i])


    def makeStandard(self):

        if self.isStandard:
            
            print("The problem is already standard.")

        else:
            
            self.makeRhsPositive()
            
            for i in range(len(self.lhs)):
                
                if self.dir[i] == "LE":
                    self.addSlackVar(i)
                    self.varNames.append(f"S{i+1}")

                elif self.dir[i] == "GE":
                    self.addSurplusVar(i)
                    self.varNames.append(f"S{i+1}")
                    self.addArtificialVar(i)
                    self.varNames.append(f"R{i+1}")

                else:
                    self.addArtificialVar(i)
                    self.varNames.append(f"R{i+1}")

            self.isItStandard = True
            
        return self.varNames
            

    def getEnterVarIndex(self):

        if self.opt == "MAX":
            
            self.value = self.obj.max()
            self.index = self.obj.argmax()

            if self.value <= 0:
                self.isOptimized = True
                
            else:
                return self.index

        else:
            self.value = self.obj.min()
            self.index = self.obj.argmin()

            if self.value >= 0:
                self.isOptimized = True

            else:
                return self.index


    def getExitVarIndex(self):

        self.theRow = self.lhs[:, self.getEnterVarIndex()]
        self.ratios = self.rhs / self.theRow

        for i in range(len(self.ratios)):
            if self.ratios[i] < 0:
                self.ratios[i] = np.inf

        return self.ratios.argmin()


    def update(self):

        self.rowIndex = self.getExitVarIndex()

        self.pivot = self.lhs[self.rowIndex][self.getEnterVarIndex()]
        
        self.lhs[self.rowIndex] = np.divide(self.lhs[self.rowIndex], self.pivot)
        
        self.rhs[self.rowIndex] = np.divide(self.rhs[self.rowIndex], self.pivot)
        
        for i in range(len(self.lhs)):
            
            if i != self.rowIndex:
                
                self.n = self.lhs[i][self.getEnterVarIndex()]

                self.lhs[i] = self.lhs[i] - self.n * self.lhs[self.rowIndex]
                self.rhs[i] = self.rhs[i] - self.n * self.rhs[self.rowIndex]

        self.n = self.obj[self.getEnterVarIndex()]
        self.obj = self.obj - self.n * self.lhs[self.rowIndex]

        self.objValue = np.add(self.objValue, self.n * self.rhs[self.rowIndex])
        
        
    def singleIteration(self):
        
        if self.isOptimized == True:
            print("The problem is optimized")
            
        else:
            self.update()
            
            

obj = np.array([5,10])
lhs = np.array([[3,6], [8,6], [2,3]])
rhs = np.array([120, 240, 210])
dir = ["LE", "LE", "LE"]
opt = "MAX"
s = Simplex(obj, lhs, rhs, dir, opt)