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

PINSETUP_DEFAULT = (D14, D27, D26, D25, D13, D21, D22, D23)
PINSETUP_COMPACT_D15D02 = (D15, D2, D0, D4, D16, D17, D5, D18)

NROWS = 4
VALUES_R1 = ("1", "2", "3", "A")
VALUES_R2 = ("4", "5", "6", "B")
VALUES_R3 = ("7", "8", "9", "C")
VALUES_R4 = ("*", "0", "#", "D")

COLS = (VALUES_R1, VALUES_R2, VALUES_R3, VALUES_R4)

class KeyPad():
    def __init__(self, pinTuple = PINSETUP_DEFAULT):
        self._pins = []
        
        ctr = 0
        for x in pinTuple:
            self._pins.append(x)
            
            #I primi 4 contatti da sx, cioè da 7 a 4, sono rows -> OUTPUT
            #Gli ultimi 4 contatti, cioè da 3 a 0, sono cols -> INPUT_PULLDOWN
            pinMode(self._pins[-1], INPUT_PULLDOWN) if (ctr > 3) else pinMode(self._pins[-1], OUTPUT)
            ctr += 1
    
    def scan(self):
        global lastChangeTime
        
        nowTime = timers.now()
        if(nowTime-lastChangeTime > 10):
            lastChangeTime=nowTime
            if(self._readCol() != 0):
                State=self._readCol()
                return State
    
    def _readRow(self, rowNumber, colValuesTuple):
        self._setRow(rowNumber)
        
        for x in range(NROWS):
            if(digitalRead(self._pins[x-4])):
                return colValuesTuple[x]
            
        return 0
    
    def _readCol(self):
        rowNumber = 0
        
        for col in COLS:
            buffer = self._readRow(rowNumber, col)
            if buffer != 0:
                return buffer
            rowNumber += 1

    def _setRow(self,num):
        for x in range(NROWS):
            digitalWrite(self._pins[x], HIGH) if (x == num) else digitalWrite(self._pins[x], LOW)