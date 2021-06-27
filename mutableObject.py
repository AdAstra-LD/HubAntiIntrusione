class Mutable:
    def __init__(self, value):
        self.val = [value]
    
    def get(self):
        return self.val[0]
        
    def set(self, newVal):
        self.val[0] = newVal
        
    def __str__(self):
        return str(self.val[0])