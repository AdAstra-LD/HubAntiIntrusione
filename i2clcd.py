import i2c
import streams
import __builtins__

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
#sia per leggere la CGRam che per scriverla
# 0 1 a d  d r e s 
CMD_CGRAM = 0x40            # DB6: set/get CG RAM address

#Flag che permette di impostare l'address counter sulla Disp Generator RAM
#sia per leggere la DDRam che per scriverla
CMD_DDRAM = 0x80            # DB7: set/get DD RAM address

RSmode_DATA = 0x01     # Mode - Sending data
RSmode_CMD = 0x00      # Mode - Sending command

# Character selector code for custom characters in CGRAM
CGRAM_CHAR = (b'\x00', b'\x01', b'\x02', b'\x03', b'\x04', b'\x05', b'\x06', b'\x07')

class I2CLCD():
    def __init__(self, i2cObj, lcd_cols=16, lcd_rows = 2):
        #LCD class constructor
        
        #i2cObj:        object of I2C class, with communication already inited and started
        #lcd_rows:      LCD rows count - e.g. 2 for LCD1602 and LCD2002, 4 for LCD2004
        #lcd_cols:      width [in characters] of the LCD - e.g. 16 for LCD1602, 20 for LCD2002/2004
        
        self.communicPort = i2cObj
        self.nCols = lcd_cols
        self.nRows = lcd_rows
        
        self.backlight = True
        self.lastData = 0x00
        self.cursorPos = (0, 0)
        
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

    def prepare(self):
        #Inizializzazione

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
        
        #Imposta LCD in modalità 4 bit
        self.i2cWrite(SETFUNC)
        self.pulseEn()

        self.sendByte(SETFUNC | SETFUNC_2LINES, RSmode_CMD)             # 00101000 Function set: interface 4bit, 2 lines, 5x8 font
        self.sendByte(CMD_DISPLAY_CTRL | CMD_DISPLAY_ON, RSmode_CMD)       # 00001100 Display ON/OFF: display on, cursor off, cursor blink off
        self.sendByte(CMD_ENTRY_MODE | CMD_ENTRY_INC, RSmode_CMD)          # 00000110 Entry Mode set: increment cursor pos [don't shift display]
        self.clear()
        
    def returnHome(self):
        #"""
        #Reset cursor and display to the original position.
        #"""
        self.sendByte(CMD_HOME, RSmode_CMD)
        self.cursorPos = (0, 0)
        sleep(2)

    def clear(self):
        #"""
        #Clear the display and reset the cursor position
        #"""
        self.sendByte(CMD_CLR, RSmode_CMD)
        sleep(2)

#----------------------------------------------------------#
# ----------------- FUNZIONI ALTO LIVELLO ---------------- #
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
    
    def setCursor(self, showCur, blinkCur):
        #Set whether the cursor is visible and whether it will blink
        cmd = CMD_DISPLAY_CTRL | CMD_DISPLAY_ON | (showCur * CMD_CURSOR_ON) | (blinkCur * CMD_CURSOR_BLINK) 
        self.sendByte(cmd, RSmode_CMD)
        
    def displayOnOff(self, status):
        #Set whether the display should be blanked or un-blanked
        self.sendByte(CMD_DISPLAY_CTRL | status * CMD_DISPLAY_ON, RSmode_CMD)

    def moveCursor(self, column, row):
        #Move the cursor to a new posotion
        #indices are always zero-based

        self.cursorPos = (column, row)
        
        #x -> col
        addr = self.cursorPos[0] & 0x3f     # Limit col index to a maximum of 63
        
        #y -> row
        if (self.cursorPos[1] & 0b00000001): # Lines 1 & 3 (x1, i.e.: 01 and 11)
            addr += 0x40    
        if (self.cursorPos[1] & 0b00000010): # Lines 2 & 3 (1x, i.e.: 10 and 11)
            addr += 0x14
            
        self.sendByte(CMD_DDRAM | addr, RSmode_CMD)

    def shift(self, direction='RIGHT', movementType="MOVECURSOR"):
        #Move the cursor and display left or right
        #direction:      could be 'RIGHT' (default) or 'LEFT'
        #movementType:   specifica se muovere display e cursore o solo cursore
        shiftRight = direction == "RIGHT"
        moveDisplay = movementType == "MOVEDISPLAY"
        
        self.cursorPos = (min(self.nCols, self.cursorPos[0] + 1), self.cursorPos[1]) if shiftRight else (max(0, self.cursorPos[0] - 1), self.cursorPos[1])
        cmd = CMD_MOVE | (shiftRight * CMD_MOVE_RIGHT) | (moveDisplay * CMD_MOVE_DISP)
        self.sendByte(cmd, RSmode_CMD)
        
    def writeCGRAM(self, charTuple, CGRAMslot=0):
        #Write a custom character to a chosen CGRAM slot
        
        #charTuple:     tuple of 8 bytes, which stores the character model data
        #CGRAMslot:     int from 0 to 7, to select the CGRAM slot in which to write the new char model
        
        CGRAMslot &= 7 #Limit CGRAM location selection to a max of 7
        self.sendByte(CMD_CGRAM | (CGRAMslot << SHIFT_CGRAM), RSmode_CMD)
        
        for charRow in charTuple:
            self.sendByte(charRow, RSmode_DATA)
            
        self.moveCursor(self.cursorPos[0], self.cursorPos[1]) #Re-stating the cursor position is necessary
        
    def print(self, text, delay = 0, updateCursorPos = False):
        #Print a string at the current cursor position
        #text:              bytes or str object, str object will be encoded with ASCII
        #delay:             adds an additional delay between a char and another
        #updateCursorPos:   when True, it also updates the cursor's coordinates tuple
        
        byteArrayString = bytearray(text[:self.nCols])
        
        if (delay == 0):
            for b in byteArrayString:
                self.sendByte(b, RSmode_DATA)
        else:
            for b in byteArrayString:
                self.sendByte(b, RSmode_DATA)
                sleep(delay)
        
        if (updateCursorPos):
            strLen = len(byteArrayString)
            self.moveCursor(strLen%self.nCols, strLen//self.nCols)
            
    def printAt(self, colID, rowID, text):
        #Stampa text ad una specifica posizione sul display e mantiene
        #quella posizione in memoria come corrente, per scritture future
        
        self.moveCursor(colID, rowID)
        self.print(text)

    def printLine(self, text, row = 0, align='LEFT', delay = 0):
        #Stampa text come frase intera sull'LCD, andando a capo automaticamente.

        #text:      bytes or str object, str object will be encoded with ASCII
        #row:       row number is zero-based
        #align:     could be 'LEFT' | 'L' (default), 'RIGHT' | 'R' or 'CENTER' | 'CENTRE' | 'C'
        
        strLen = len(text)
        rowsToPrint = round(strLen/self.nCols)
        
        for x in range (rowsToPrint):
            
            currentLine = text[:self.nCols].strip()
            whitespace = self.nCols - strLen
            __builtins__.print("currentLine = " + currentLine)
            
            if align == 'LEFT' or align == 'L':
                currentLine = currentLine + b' ' * whitespace
            elif align == 'RIGHT' or align == 'R':
                currentLine = b' ' * whitespace + currentLine
            elif align == 'CENTER' or align == 'CENTRE' or align == 'C':
                currentLine = b' ' * (whitespace // 2) + currentLine + b' ' * (whitespace // 2)
            
            #self.sendByte(LCD_ROWS[(x+row) % self.nRows], RSmode_CMD)
            self.moveCursor(0, (x+row) % self.nRows)
            __builtins__.print("moved cursor to :  " + str(self.cursorPos[0]) + ",  " + str((x+row) % self.nRows))
            self.print(currentLine, delay)
            text = text[self.nCols:].strip()
        
        #self.moveCursor(strLen % self.nCols, strLen//self.nCols + (row % self.nRows))