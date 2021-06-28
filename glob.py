import threading
import mutableObject as mo

#Alarm Keywords
temperatureKey = 'temperature'
humidityKey = 'humidity'
lightKey = 'light'

#Peripherals
lcd = None
pad = None
photoresistor = None

#Utilities
def isNumber(s):
    if s == None:
        return False
        
    try:
        int(s)
        return True
    except ValueError:
        return False

def stringRpad(string, desiredLength, filler = " "):
    strlen = len(string)
    
    if strlen < desiredLength:
        string = string + (filler * (desiredLength-strlen))

    return string

def stringCapitalize(string):
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
            for x in range (ceil(len(stringCopy) / nCols)):
                stringList.append(stringCopy[:nCols].strip())
                stringCopy = stringCopy[nCols:]
        else:
            stringList.append(stringCopy[:posBackslash].strip())
            stringCopy = stringCopy[(posBackslash+1):]
            
        #__builtins__.print("Ho aggiunto la stringa " +  '"' + str(stringList[len(stringList)-1] + '"'))
        
    return stringList

def ceil(n):
    return -int((-n) // 1)

def max(n1, n2):
    if (n1 > n2):
        return n1
        
    return n2

def pinToggle_wrapper(pin):
    pinToggle(pin)

def flashPins(flashFrequency, condition, pin, taskSequenceOnEnd = [], endArgs = [[]]):
    if (flashFrequency == 0):
        flashFrequency = 1
    
    thread(timedRepeat, 1000//flashFrequency, condition, 
        [pinToggle_wrapper], [[pin]], 
        taskSequenceOnEnd, endArgs)


    #timePeriod: tempo che passa tra una chiamata di tutti i task iniziali e l'altra
    #runCondition: condizione che consente di iterare ed eseguire i task iniziali
    
    #taskSequenceOnStart: lista di n puntatori alle funzioni iniziali da eseguire in ordine di inserimento
    #startArgs: lista contenente n liste di argomenti, associate alle funzioni iniziali (nello stesso ordine)
    
    #taskSequenceOnEnd: lista di m puntatori alle funzioni da eseguire (in ordine di inserimento) una volta che runCondition decade. 
    #startArgs: lista contenente m liste di argomenti, associate alle funzioni finali (nello stesso ordine)

    #ESEMPIO:
    #timedRepeat(12500, continuaAdOperare, [somma, sottrai], [[2, 3], [10, 8]], stampaRisultato, [[]])
    
    #ad intervalli regolari di 12.5 secondi, a meno che "continuaAdOperare" non diventi False, vengono eseguite le funzioni:
    #somma(2, 3)
    #sottrai(10, 8)

    #non appena "continuaAdOperare" è False, viene eseguita stampaRisultato()
def timedRepeat(timePeriod, runCondition, taskSequenceOnStart, startArgs = [[]], taskSequenceOnEnd = [], endArgs = [[]], eventWait = None):
    if (eventWait is not None):
        eventWait.wait()
    
    numStartTasks = len(taskSequenceOnStart)
    while runCondition.get() == True:
        for x in range(numStartTasks):
            taskSequenceOnStart[x](*startArgs[x])
            
        sleep(timePeriod)
    
    #Una volta finito il loop...
    numFinalTasks = len(taskSequenceOnEnd)
    if (taskSequenceOnEnd is not None and numFinalTasks > 0):
        for x in range(numFinalTasks):
            taskSequenceOnEnd[x](*(endArgs[x]))
