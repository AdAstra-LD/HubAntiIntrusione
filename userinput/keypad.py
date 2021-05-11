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

lastChangeTime=0
keyPressed=0

PINSETUP_DEFAULT =                      (D14, D27, D26, D25, D13, D21, D22, D23)
PINSETUP_COMPACT_D15D02 =               (D15, D2, D0, D4, D16, D17, D5, D18)
PINSETUP_GPIOEXT_D15__D05 =             (D15, D2, D0, D4, D5, D18, D19, D21)

NUM_ROWS = 4
NO_BUTTON_PRESSED = -1

VALUES_R1 = ("1", "2", "3", "A")
VALUES_R2 = ("4", "5", "6", "B")
VALUES_R3 = ("7", "8", "9", "C")
VALUES_R4 = ("*", "0", "#", "D")

COLS = (VALUES_R1, VALUES_R2, VALUES_R3, VALUES_R4)

lastValue = ""

class KeyPad():
    def __init__(self, pinTuple = PINSETUP_DEFAULT):
        self._pins = []
        
        ctr = 0
        for x in pinTuple:
            self._pins.append(x)
            
            #I primi 4 contatti da sx, cioè da 7 a 4, sono rows -> OUTPUT 
            # DEVONO AVERE ADC!!!!
            
            #Gli ultimi 4 contatti, cioè da 3 a 0, sono cols -> INPUT_PULLDOWN
            
            #O O O O  I I I I
            pinMode(self._pins[-1], INPUT_PULLDOWN) if (ctr > 3) else pinMode(self._pins[-1], OUTPUT)
            ctr += 1
    
    def scan(self):
        global lastChangeTime
        
        while True:
            nowTime = timers.now()              #Ottieni millisecondi passati dall'avvio del programma
            if(nowTime-lastChangeTime > 10):    #se ne sono passati almeno 10
                lastChangeTime=nowTime          #aggiorna il tempo 
                status = self._readCol()        #scansiona pressioni
                
                if status != lastValue:         #evita duplicati
                    lastValue = status
                    
                    if status != None:
                        return status

    def _readCol(self):
        colNumber = 0
        
        for col in COLS:
            buffer = self._readRow(colNumber, col)
            
            if buffer != NO_BUTTON_PRESSED:
                return buffer
                
            colNumber += 1
        
        #Restituisce NONE se non rileva pressioni
    
    def _readRow(self, rowNumber, charTuple):
        self._setRow(rowNumber)
        
        for x in range(NUM_ROWS):
            if(digitalRead(self._pins[-4 + x])): #Leggi il 4-ultimo, poi il 3-ultimo, poi il penultimo
                return charTuple[x] # Appena leggi valore alto, restituisci il carattere associato
        
        return NO_BUTTON_PRESSED

    def _setRow(self, num):
        for x in range(NUM_ROWS):
            digitalWrite(self._pins[x], HIGH) if (x == num) else digitalWrite(self._pins[x], LOW)