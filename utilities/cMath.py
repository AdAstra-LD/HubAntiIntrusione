def ceil(n):
    return -int((-n) // 1)

def max(n1, n2):
    if (n1 > n2):
        return n1
        
    return n2
    
def isNumber(s):
    if s == None:
        return False
        
    try:
        int(s)
        return True
    except ValueError:
        return False