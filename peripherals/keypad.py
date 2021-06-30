########ESEMPIO#############
############################
#import keypad as padlib
#import streams
#streams.serial()
#
#def key():
#    keyvalue=kpad.scan()
#    if keyvalue != None:
#        print(keyvalue)
#        sleep(300)
#        return keyvalue
#        
#kpad=padlib.KeyPad(padlib.PINSETUP_COMPACT_D12D14)
#
#print("I'm ready")
#while True:
#    key()
############################

import timers

lastChangeTime = 0
keyPressed = 0

PINSETUP_DEFAULT = (D19, D18, A0, A1, D27, D14, D12, D13)

NUM_ROWS = 4
NO_BUTTON_PRESSED = -1

VALUES_R1 = ("1", "2", "3", "A")
VALUES_R2 = ("4", "5", "6", "B")
VALUES_R3 = ("7", "8", "9", "C")
VALUES_R4 = ("*", "0", "#", "D")

COLS = (VALUES_R1, VALUES_R2, VALUES_R3, VALUES_R4)

lastValue = ""

class KeyPad():
    def __init__(self, pinTuple = PINSETUP_DEFAULT, invert = False):
        self._pins = []
        
        if invert:
            pinTuple = reversed(pinTuple)
        
        ctr = 0
        for x in pinTuple:
            self._pins.append(x)
            
            #I primi 4 contatti da sx, cioè da 8 a 5, sono rows -> OUTPUT 
            # DEVONO AVERE ADC!!!!
            
            #Gli ultimi 4 contatti, cioè da 4 a 1, sono cols -> INPUT_PULLDOWN
            
            #O O O O  I I I I
            pinMode(self._pins[-1], INPUT_PULLDOWN) if (ctr > 3) else pinMode(self._pins[-1], OUTPUT)
            ctr += 1
    
    def scan(self, validChars = None):
        ##DOCUMENTARE!!!
        
        global lastChangeTime
        
        while True:
            nowTime = timers.now()              #Ottieni millisecondi passati dall'avvio del programma
            if(nowTime-lastChangeTime > 10):    #se ne sono passati almeno 10
                lastChangeTime=nowTime          #aggiorna il tempo 
                value = self._readCol()        #scansiona pressioni
                
                if value != lastValue:         #evita duplicati
                    lastValue = value
                    
                    if value != None:
                        if validChars == None:
                            return value
                        else:
                            if value in validChars:
                                return value

    def _readCol(self):
        rowNumber = 0
        buffer = None
        
        for charTuple in COLS:
            buffer = self._readRow(rowNumber, charTuple)
            
            if buffer != NO_BUTTON_PRESSED:
                return buffer
                
            rowNumber += 1
        
        #Restituisce NONE se non rileva pressioni
    
    def _readRow(self, rowNumber, charTuple):
        for x in range(NUM_ROWS):
            digitalWrite(self._pins[x], HIGH) if (x == rowNumber) else digitalWrite(self._pins[x], LOW)
        
        for x in range(NUM_ROWS):
            if(digitalRead(self._pins[-4 + x])): #Leggi il 4-ultimo, poi il 3-ultimo, poi il penultimo
                return charTuple[x] # Appena leggi valore alto, restituisci il carattere associato
        
        return NO_BUTTON_PRESSED