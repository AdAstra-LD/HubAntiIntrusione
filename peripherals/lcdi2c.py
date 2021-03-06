import i2c
import streams
import threading

import utilities.cString as cString

# I2C byte:   [H ------------------------ L]
#             [  bit dati  ] [bit controllo]
# LCD1602:    D7  D6  D5  D4  BT  E  R/W  RS

# ROW_1 = 0x80   # LCD RAM address for the 1st line
# ROW_2 = 0xC0   # LCD RAM address for the 2nd line
# ROW_3 = 0x94   # LCD RAM address for the 3rd line
# ROW_4 = 0xD4   # LCD RAM address for the 4th line
# LCD_ROWS = (0x80, 0xC0, 0x94, 0xD4)

# Masks and Shift values
MASK_EN = 0b00000100
SHIFT_CGRAM = 3
SHIFT_BACKLIGHT = 3
SHIFT_DATA = 4



# LCD controller command set
CMD_CLR = 0x01              # DB0: clear display
CMD_HOME = 0x02             # DB1: return to home position

#0 0 0 0  0 1 Inc/Dec Shift
CMD_ENTRY_MODE = 0x04       # DB2: set entry mode
CMD_ENTRY_INC = 0x02        # --DB1: increment
CMD_ENTRY_SHIFT = 0x01      # --DB0: shift

#0 0 0 0  1 Disp Curs Blink
CMD_DISPLAY_CTRL = 0x08     # DB3: turn lcd/cursor on
CMD_DISPLAY_ON = 0x04       # --DB2: turn display on
CMD_CURSOR_ON = 0x02        # --DB1: turn cursor on
CMD_CURSOR_BLINK = 0x01     # --DB0: blinking cursor

#0 0 0 1  Shift Right/Left X X
#Shift = 0, Right = 0 -> Shift cursore a sx 
#Shift = 0, Right = 1 -> Shift cursore a dx 
#Shift = 1, Right = 0 -> Shift display a sx, il cursore segue lo shift 
#Shift = 1, Right = 1 -> Shift cursore a sx, il cursore segue lo shift
CMD_MOVE = 0x10             # DB4: move cursor/display
CMD_MOVE_DISP = 0x08        # --DB3: move display (0-> move cursor)
CMD_MOVE_RIGHT = 0x04       # --DB2: move right (0-> left)

#0 0 1 8bit    TwoLines 5x10Mode X X
SETFUNC = 0x20              # DB5: function set
SETFUNC_8BIT = 0x10         # --DB4: set 8BIT mode (0->4BIT mode)
SETFUNC_2LINES = 0x08       # --DB3: two lines (0->one line)
SETFUNC_5BY10 = 0x04        # --DB2: 5x10 font (0->5x8 font)
CMD_RESETFUNC = 0x30        # See "Initializing by Instruction" section

#Flag che permette di impostare l'address counter sulla Char Generator RAM
#sia per leggere la CGRAM che per scriverla
# 0 1 a d  d r e s 
CMD_CGRAM = 0x40            # DB6: set/get CG RAM address

#Flag che permette di impostare l'address counter sulla Display data RAM
#sia per leggere la DDRAM che per scriverla
CMD_DDRAM = 0x80            # DB7: set/get DD RAM address

RSmode_DATA = 0x01     # Mode - Sending data
RSmode_CMD = 0x00      # Mode - Sending command

########################################
all = 0b11111
nul = 0

#Communication
SMILEY_FACE =       (nul, 0b01010, 0b01010, nul, 0b10001, 0b01110, nul, nul)
SAD_FACE =          (nul, 0b01010, 0b01010, nul, 0b01110, 0b10001, nul, nul)
#POKER_FACE =        (nul, 0b01010, 0b01010, nul, all, nul, nul, nul)
#EXCLAMATION =       (0b00100, 0b01110, 0b01110, 0b01110, 0b00100, nul, 0b00100, nul)
#ARROW_UP =          (0b00100, 0b01110, all, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100)
#ARROW_DOWN =        (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, all, 0b01110, 0b00100)

#Ambient
#SUN =               (0b10101, 0b01110, all, all, 0b01110, 0b10101, nul, nul)
#CLOUD =             (nul, 0b01110, 0b10001, all, nul, 0b01010, 0b00101, nul)
#RAIN =              (nul, 0b01110, 0b10001, all, nul, nul, nul, nul)
#SNOW =              (nul, 0b00100, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b00100)

TEMPERATURE =       (0b00100, 0b01010, 0b01111, 0b01010, 0b01010, 0b10001, 0b10001, 0b01110)
HUMIDITY =          (nul, 0b00100, 0b01110, 0b01110, 0b11101, 0b11011, 0b10111, 0b01110)
LIGHT =             (0b00100, 0b10001, 0b00100, 0b01110, 0b01110, 0b00100, 0b10001, 0b00100)

CELSIUS =           (0b11100, 0b10100, 0b11100, nul, 0b00111, 0b00100, 0b00100, 0b00111)
#FAHRENHEIT =        (0b11100, 0b10100, 0b11100, nul, 0b00111, 0b00110, 0b00100, 0b00100)

#Connectivity
WIFI =              (nul, 0b01110, 0b10001, 0b00100, 0b01010, nul, 0b00100, nul)
NO_SIGNAL =         (0b01010, 0b00100, 0b01010, nul, 0b00001, 0b00001, 0b00101, 0b10101)
MQTT =              (nul, 0b00001, 0b11100, 0b00010, 0b11001, 0b00101, 0b10101, nul)

#Security
UNLOCKED =          (0b01110, 0b00001, 0b00001, all, all, 0b11011, 0b11011, all)
LOCKED =            (0b01110, 0b10001, 0b10001, all, all, 0b11011, 0b11011, all)

#Misc
#ADASTRA =           (0b11011, 0b10001, 0b10110, 0b00100, 0b01100, 0b01101, 0b10001, 0b11011)

###################################
# To use with (lcd.send_bytes, RSMODE_DATA)
#ARROW_RIGHT =       0b01111110
#ARROW_LEFT =        0b01111111
#
#ALPHA =             0b11100000
#BETA =              0b11100010
#DEGREE =            0b11011111
#DIVISION =          0b11111101
###################################

class LCDI2C():
    def __init__(self, commPort, address = 0x27, clock = 100000, nCols=16, nRows = 2):
        #LCD class constructor
        
        #i2cObj:    object of I2C class, with communication already inited and started
        #nRows:     LCD rows count - e.g. 2 for LCD1602 and LCD2002, 4 for LCD2004
        #nCols:     width [in characters] of the LCD - e.g. 16 for LCD1602, 20 for LCD2002/2004
        
        #Segnalatore di posizione CGRAM
        self.CGRAM = (b'\x00', b'\x01', b'\x02', b'\x03', b'\x04', b'\x05', b'\x06', b'\x07')

        self.nCols = nCols
        self.nRows = nRows
        
        self.backlight = True
        self.lastData = 0x00
        self.lastPrinted = ""
        self.cursorPos = [0, 0]
        self.i2cport = commPort
        self.lock = threading.Lock()
        
        if self.i2cport is None:
            return
        
        ### CRITICO - ISTANZA DI I2C ###
        self.communicPort = i2c.I2C(self.i2cport, address, clock)
        
    def prepare(self):
        #Inizializzazione
        if self.i2cport is None:
            return
        
        self.communicPort.start()
        #Diamo un po' di tempo all'LCD per accendersi del tutto
        sleep(20) 
        
        #Inizia sequenza di preparazione
        self.i2cWrite(CMD_RESETFUNC)
        self.pulseEn()
        sleep(5)
        
        self.i2cWrite(CMD_RESETFUNC)
        self.pulseEn()
        sleep(105, MICROS)
        
        self.i2cWrite(CMD_RESETFUNC)
        self.pulseEn()
        sleep(105, MICROS)
        
        #Imposta LCD in modalit?? 4 bit
        self.i2cWrite(SETFUNC)
        self.pulseEn()
        
        self.displayConfig()                 # 0001 1100 Function set: interface 4bit, 2 lines, 5x8 font
        self.cursorConfig()                  # 0000 1100 Display ON/OFF: display on, cursor off, cursor blink off
        self.inputResponseConfig()           # 00000110 Entry Mode set: increment cursor pos [don't shift display]
        self.clear()
        
    def i2cWrite(self, data):
        #"""write one byte to I2C bus"""
        self.lastData = data
        self.communicPort.write(data)
    
    def pulseEn(self):
        #"""perform a high level pulse to EN"""
        self.i2cWrite(self.lastData | MASK_EN)
        sleep(3)
        self.i2cWrite(self.lastData & ~MASK_EN)
        sleep(3)

    def sendByte(self, data, RSmode):
        #"""write one byte to LCD"""

        data_H = (data & 0xF0) | (self.backlight << SHIFT_BACKLIGHT) | RSmode
        self.i2cWrite(data_H)
        self.pulseEn()

        data_L = ((data << SHIFT_DATA) & 0xF0) | (self.backlight << SHIFT_BACKLIGHT) | RSmode
        self.i2cWrite(data_L)
        self.pulseEn()

        sleep(100, MICROS)
    
    def stop(self):
        self.communicPort.stop()
#----------------------------------------------------------#
# FUNZIONI DI INIZIALIZZAZIONE ----------------------------#
#----------------------------------------------------------#
    def returnHome(self):
        #"""
        #Reset cursor and display to the original position.
        #"""
        self.sendByte(CMD_HOME, RSmode_CMD)
        self.cursorPos = [0, 0]
        sleep(2)

    def clear(self):
        #"""
        #Clear the display and reset the cursor position
        #"""
        if self.i2cport is None:
            return
        
        self.sendByte(CMD_CLR, RSmode_CMD)
        self.cursorPos = [0, 0]
        sleep(2)
        
#----------------------------------------------------------#
# FUNZIONI DI CONFIGURAZIONE DISPLAY ----------------------#
#----------------------------------------------------------#
    def displayConfig(self, eightBitMode = False, twoLines = True, fiveBy10 = False):
        self.sendByte(SETFUNC | 
        eightBitMode * SETFUNC_8BIT | 
        twoLines * SETFUNC_2LINES | 
        fiveBy10 * SETFUNC_5BY10, RSmode_CMD)

    def inputResponseConfig(self, incrementPos = True, shiftDisplay = False):
        #incrementPos:      1 = increment/shiftLeft. 0 = decrement/shift right
        #shiftDisplay:      sets whether to shift display or not
        
        self.sendByte( CMD_ENTRY_MODE | 
        incrementPos * CMD_ENTRY_INC | 
        shiftDisplay * CMD_ENTRY_SHIFT, RSmode_CMD)

#----------------------------------------------------------#
# FUNZIONI BACKLIGHT --------------------------------------#
#----------------------------------------------------------#
    def setBacklight(self, status):
        #Imposta LCD backlight
        self.backlight = status
        i2c_data = (self.lastData & 0xF7) + (status << SHIFT_BACKLIGHT)
        self.i2cWrite(i2c_data)
        
    def toggleBacklight(self):
        #Spegne LCD backlight se accesa, la accende se spenta
        status = self.backlight
        self.setBacklight(not status)
    
    def flashDisplay(self, times, delay):
        #makes backlight flash a given number of times with the specified delay
        for x in range(2*times):
            self.toggleBacklight()
            sleep(delay)
        
#----------------------------------------------------------#
# FUNZIONI CURSORE ----------------------------------------#
#----------------------------------------------------------#
    def cursorConfig(self, displayOnOff = True, showCursor = False, blinkCursor = False):
        #displayOnOff:      sets whether the display should be blanked or un-blanked
        #showCursor:        sets whether to display cursor or not
        #showCursor:        sets whether to display blinking cursor or not (it will have no effect if showCursor is False)
        
        self.sendByte( CMD_DISPLAY_CTRL | 
        displayOnOff * CMD_DISPLAY_ON | 
        showCursor * CMD_CURSOR_ON | 
        blinkCursor * CMD_CURSOR_BLINK, RSmode_CMD)
        
    def shift(self, shamt = 1, delay = -1):
        #Moves the cursor by shamt positions, with a specified delay for each shift
        
        #shamt:             shift amount
        #delay:             sleep time between one shift and the other. ignored if shamt is 1
        
        
        #Se il cursore sta gi?? al bordo dello schermo, lo shift lo far?? sparire!!!!!!!!!
        if shamt == 0:
            return
        
        if delay < 0:
            delay = 120
        
        if self.cursorPos[0] + shamt > self.nCols -1 or self.cursorPos[0] + shamt < 0:
            return
        else:
            if delay > 0:
                if shamt >= 0:
                    amt = 1
                else:
                    amt = -1
                    
                for x in range(abs(shamt)):
                    self.moveCursor(self.cursorPos[0]+amt, self.cursorPos[1])
            else:
                self.moveCursor(self.cursorPos[0]+shamt, self.cursorPos[1])
        
    def getCursorPos(self):
        return self.cursorPos
    
    def moveCursor(self, column, row):
        #Move the cursor to a new posotion
        #indices are always zero-based
        
        #x -> col
        addr = column & 0x3f     # Limit col index to a maximum of 63
        
        #y -> row
        if row & 0b00000001: # Lines 1 & 3 (x1, i.e.: 01 and 11)
            addr += 0x40    
        if row & 0b00000010: # Lines 2 & 3 (1x, i.e.: 10 and 11)
            addr += 0x14
        
        self.sendByte(CMD_DDRAM | addr, RSmode_CMD)
        self.cursorPos = [column, row]
        
#----------------------------------------------------------#
# FUNZIONI SCRITTURA --------------------------------------#
#----------------------------------------------------------#
    
    def writeCGRAM(self, charTuple, CGRAMslot=0):
        #Write a custom character to a chosen CGRAM slot
        
        #charTuple:     tuple of 8 bytes, which stores the character model data
        #CGRAMslot:     int from 0 to 7, to select the CGRAM slot in which to write the new char model
        
        CGRAMslot &= 7  #Limit CGRAM location selection to a max of 7
        self.sendByte(CMD_CGRAM | (CGRAMslot << SHIFT_CGRAM), RSmode_CMD)
        
        for charRow in charTuple:
            self.sendByte(charRow, RSmode_DATA)
            
        self.moveCursor(self.cursorPos[0], self.cursorPos[1]) #Re-stating the cursor position is necessary
        
    def print(self, text, row = None, align = None, delay = 0):
        #Stampa una stringa su LCD
        #row:               riga di schermo su cui stampare. La posizione orizzontale resta invariata. se None, usa la riga corrente
        #align:             allineamento del testo ad un riferimento, senza cambiare riga. se None, l'allineamento non viene utilizzato.
        #text:              bytes o stringa da stampare
        #delay:             delay tra la stampa di un char e l'altra
        
        if self.i2cport is None:
            return
        
        byteArrayString = bytearray(text[:self.nCols])
        strLen = len(byteArrayString)
        
        if row is not None:
            self.moveCursor(self.cursorPos[0], row%self.nRows)
        
        #### DO NOT CHANGE ORDER OF ADDITION ####
        if align is not None:
            align = align.upper()
            if align == 'LEFT' or align == 'L' or align == "SINISTRA":
                self.moveCursor(0, self.cursorPos[1])
            elif align == 'RIGHT' or align == 'R' or align == "DESTRA":
                self.moveCursor(self.nCols-strLen, self.cursorPos[1])
            elif align == 'CENTER' or align == 'CENTRE' or align == 'C' or align == "CENTRO":
                self.moveCursor((self.nCols-strLen)//2, self.cursorPos[1])
        
        if delay == 0:
            for b in byteArrayString:
                self.sendByte(b, RSmode_DATA)
        else:
            for b in byteArrayString:
                self.sendByte(b, RSmode_DATA)
                sleep(delay)
        
        
        self.lastPrinted = byteArrayString
        
        self.cursorPos[0] += strLen%self.nCols
        self.cursorPos[1] += strLen//self.nCols
        
        sleep(50)
        
            
    def printAtPos(self, text, colID, rowID, delay = 0):
        #Stampa text ad una specifica posizione sul display e mantiene
        #quella posizione in memoria come corrente, per scritture future
        
        self.moveCursor(colID, rowID)
        self.print(text, delay = delay)
    
    def printLine(self, text, row = 0, align='LEFT', delay = 0, sentenceDelay = 1500, clearPrevious = True):
        #Stampa text come frase intera sull'LCD, andando a capo automaticamente.
        #row:               riga di schermo su cui stampare. 
        #text:              bytes o stringa da stampare
        #delay:             delay tra la stampa di un char e l'altra
        #align:     could be 'LEFT' | 'L' (default), 'RIGHT' | 'R' or 'CENTER' | 'CENTRE' | 'C'
        
        #NOTE:  pu?? essere migliorata aggiungendo un controllo sulla lunghezza della prossima parola e,
        #       se pi?? lunga dello spazio rimasto sulla riga, stamparla a capo. (auto word-wrap)
        
        if self.i2cport is None:
            return
        
        rowsToPrint = cString.splitSentence(text, self.nCols)
        numRowsToPrint = len(rowsToPrint)
        
        currentLine = ""
        whitespaceCount = 0
        for r in range (numRowsToPrint):
            currentLine = rowsToPrint[r]
            strLen = len(currentLine)
            if (strLen < 2 && currentLine[0] != '\n'):
                continue
            
            if r % self.nRows == 0:
                if r != 0 and numRowsToPrint >= self.nRows:
                    #__builtins__.print("Sleeping sentenceDelay")
                    sleep(sentenceDelay)
                    
                if clearPrevious:
                    self.clear()
            
            whitespaceCount = self.nCols - strLen
            #__builtins__.print( "currentLine = " + currentLine )
            #__builtins__.print( "la stringa da stampare ?? lunga " + str(strLen) )
            
            if align is not None:
                align = align.upper()
                #### DO NOT CHANGE ORDER OF ADDITION ####
                if align == 'LEFT' or align == 'L' or  align == "SINISTRA":
                    currentLine = currentLine + b' ' * whitespaceCount
                elif align == 'RIGHT' or align == 'R' or align == "DESTRA":
                    currentLine = b' ' * whitespaceCount + currentLine
                elif align == 'CENTER' or align == 'CENTRE' or align == 'C' or align == "CENTRO":
                    currentLine = b' ' * (whitespaceCount // 2) + currentLine + b' ' * (whitespaceCount // 2)
            
            #print current line to LCD
            self.printAtPos(currentLine, 0, (r+row) % self.nRows, delay)
            
            #__builtins__.print("ho finito di stampare, la posizione del cursore e': "   + str(self.cursorPos[0]) + ", " + str(self.cursorPos[1]))
        
        
        if align == 'LEFT' or align == 'L':
            cursorX = self.nCols - 1 - (len(currentLine) % self.nCols)
        else:
            cursorX = (len(currentLine.strip()) + whitespaceCount//2) % self.nCols
            #__builtins__.print(currentLine)
        
        
        cursorY = (numRowsToPrint-1) % self.nRows
        self.moveCursor(cursorX, cursorY)
        
        #__builtins__.print("ho spostato il cursore a: "   + str(self.cursorPos[0]) + ", " + str(self.cursorPos[1]))