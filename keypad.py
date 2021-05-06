import timers

lastChangeTime=0
keyState=0
State=0

class KeyPad(object):
    def __init__(self, row1: D14, row2: D27, row3: D26, row4: D25, col1: D13, col2: D21, col3: D22, col4: D23):
        self._pinRow1 = row1
        self._pinRow2 = row2
        self._pinRow3 = row3
        self._pinRow4 = row4
        self._pinCol1 = col1
        self._pinCol2 = col2
        self._pinCol3 = col3
        self._pinCol4 = col4
        
        pinMode(self._pinRow1, OUTPUT)
        pinMode(self._pinRow2, OUTPUT)
        pinMode(self._pinRow3, OUTPUT)
        pinMode(self._pinRow4, OUTPUT)
        pinMode(self._pinCol1, INPUT_PULLDOWN)
        pinMode(self._pinCol2, INPUT_PULLDOWN)
        pinMode(self._pinCol3, INPUT_PULLDOWN)
        pinMode(self._pinCol4, INPUT_PULLDOWN)
        
    
    def scan(self):
        global lastChangeTime
        
        nowTime = timers.now()
        if(nowTime-lastChangeTime > 10):
            lastChangeTime=nowTime
            if(self._readCol() != 0):
                State=self._readCol()
                return State
            
    def _readRow1(self):
        self._setRow(1)
        
        if(digitalRead(self._pinCol1)): #firstCol
            keyState='1'
        elif(digitalRead(self._pinCol2)): #secondCol
            keyState='2'
        elif(digitalRead(self._pinCol3)): #thirdCol
            keyState='3'
        elif(digitalRead(self._pinCol4)): #fourthCol
            keyState='A'
        else:
            keyState=0
        return keyState

    def _readRow2(self):
        self._setRow(2)
        
        if(digitalRead(self._pinCol1)):
            keyState='4'
        elif(digitalRead(self._pinCol2):
            keyState='5'
        elif(digitalRead(self._pinCol3):
            keyState='6'
        elif(digitalRead(self._pinCol4):
            keyState='B'
        else:
            keyState=0 
        return keyState

    def _readRow3(self):
        self._setRow(3)
        
        if(digitalRead(self._pinCol1)):
            keyState='7'
        elif(digitalRead(self._pinCol2)):
            keyState='8'
        elif(digitalRead(self._pinCol3)):
            keyState='9'
        elif(digitalRead(self._pinCol4)):
            keyState='C'
        else:
            keyState=0 
        return keyState
    
    def _readRow4(self):
        self._setRow(4)
        
        if(digitalRead(self._pinCol1)):
            keyState='*'
        elif(digitalRead(self._pinCol2)):
            keyState='0'
        elif(digitalRead(self._pinCol3)):
            keyState='#'
        elif(digitalRead(self._pinCol4)):
            keyState='D'
        else:
            keyState=0
        return keyState
    
    def _readCol(self):
        data_buffer1=self._readRow1()
        data_buffer2=self._readRow2()
        data_buffer3=self._readRow3()
        data_buffer4=self._readRow4()
        if (data_buffer1 != 0):
            return data_buffer1
        elif (data_buffer2 != 0):
            return data_buffer2
        elif (data_buffer3 != 0):
            return data_buffer3
        elif (data_buffer4 != 0):
            return data_buffer4

    def _setRow(self,num):
        if num==1:
            self._pinRow1.on()
            self._pinRow2.off()
            self._pinRow3.off()
            self._pinRow4.off()
        if num==2:
            self._pinRow1.off()
            self._pinRow2.on()
            self._pinRow3.off()
            self._pinRow4.off()
        if num==3:
            self._pinRow1.off()
            self._pinRow2.off()
            self._pinRow3.on()
            self._pinRow4.off()
        if num==4:
            self._pinRow1.off()
            self._pinRow2.off()
            self._pinRow3.off()
            self._pinRow4.on()