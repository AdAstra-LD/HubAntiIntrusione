class CircularList():
    def __init__(self, size = 20):
        self.container = []
        self.size = size
        
    def add(self, elem, nDecimals = 2):
        #elemStr = str(elem)
        #posDot = elemStr.find('.')
        #if posDot == -1 or len(elemStr) - posDot - 1 <= nDecimals:
        #    self.container.append(elemStr)
        #else:
        #    self.container.append(str('%.*f') % (nDecimals, elem))
        
        self.container.append(str(elem))
        self.container = self.container[-self.size:]
    
    def clear(self):
        self.container = []
        
    def __str__(self):
        return str(self.container).replace("'", "").replace("\"", "")