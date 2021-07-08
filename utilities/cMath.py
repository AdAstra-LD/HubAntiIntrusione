def ceil(n):
    return -int((-n) // 1)
    
def isNumber(s):
    if s == None:
        return False
        
    try:
        int(s)
        return True
    except ValueError:
        return False
        
def exp(b, e):
    if e > 0:
        for x in range(e-1):
            b = b*b
    elif e == 0:
        return 1
    else: #e < 0
        return 1/exp(b, -e)
    return b