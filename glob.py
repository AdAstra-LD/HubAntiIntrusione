import threading
import utilities.mutableObject as mo

#Alarm Keywords
temperatureKey = 'temperature'
humidityKey = 'humidity'
lightKey = 'light'

#Peripherals
lcd = None
pad = None
htu21d = None
photoresistor = None

#Utilities

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
####def timedRepeat(timePeriod, runCondition, eventWait, taskSequenceOnStart, startArgs = [[]], taskSequenceOnEnd = [], endArgs = [[]]):
####    
####    numStartTasks = len(taskSequenceOnStart)
####    
####    print("About to start a new process of " + str(numStartTasks) + " tasks...")
####    while runCondition.get() == True:
####        for x in range(numStartTasks):
####            eventWait.wait()
####            taskSequenceOnStart[x](*startArgs[x])
####            
####        sleep(timePeriod)
####    
####    #Una volta finito il loop...
####    numFinalTasks = len(taskSequenceOnEnd)
####    if (taskSequenceOnEnd is not None and numFinalTasks > 0):
####        for x in range(numFinalTasks):
####            taskSequenceOnEnd[x](*(endArgs[x]))
####