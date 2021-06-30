import utilities.cMath as cMath

def rpad(string, desiredLength, filler = " "):
    strlen = len(string)
    
    if strlen < desiredLength:
        string = string + (filler * (desiredLength-strlen))

    return string

def lpad(string, desiredLength, filler = " "):
    strlen = len(string)
    
    if strlen < desiredLength:
        string = (filler * (desiredLength-strlen)) + string

    return string

def capitalize(string):
    newStr = [c for c in string]
        
    newStr[0] = newStr[0].upper()
    return ''.join(newStr)

def splitSentence(sentence, nCols): 
    stringCopy = sentence
    
    stringList = []
    posBackslash = 0
    while (len(stringCopy) > 0 and posBackslash >= 0):
        #__builtins__.print(str(stringCopy)) 
        
        posBackslash = stringCopy.find('\n')
        
        #__builtins__.print("Found backslash at " + str(posBackslash))
        
        if (posBackslash < 0):
            for x in range (cMath.ceil(len(stringCopy) / nCols)):
                stringList.append(stringCopy[:nCols].strip())
                stringCopy = stringCopy[nCols:]
        else:
            stringList.append(stringCopy[:posBackslash].strip())
            stringCopy = stringCopy[(posBackslash+1):]
            
        #__builtins__.print("Ho aggiunto la stringa " +  '"' + str(stringList[len(stringList)-1] + '"'))
        
    return stringList