import memory.customflash as flash
import memory.memorymap as memmap
import userinput.keypad as pad

SYSTEM_UNINITIALIZED = 0
SYSTEM_UNPROTECTED = 1
SYSTEM_PROTECTED = 1

def userSetup(lcd, pad):
    strm = flash.FlashFileStream(memmap.ESP32_BASEADDR, 9)
    strm[0] = 0
    
    lcd.printLine("Unisa - IOT 2021\nLaiso, Macaro", align = "C")
    sleep(500)
    systemStatus = strm.read_byte()
    
    if systemStatus == SYSTEM_UNINITIALIZED:
        lcd.clear()
        
        lcd.printLine("Welcome!", align = "C")
        lcd.shift()
        lcd.print(lcd.CGRAMchar[0]) #SmileyFace
        sleep(1500)
        
        lcd.printLine("There are a few\nthings to set up")
        sleep(1500)
        
        lcd.printLine("Please choose a\npassword for the\nalarm system.")
        sleep(1500)
        
        passwordScreen(lcd, pad)

def passwordScreen(lcd, pad):
    lcd.returnHome()
    lcd.printLine("C=Cancel  D=Done", row = 1)
    lcd.returnHome()
    lcd.print("  PW: ")
    lcd.cursorConfig(True, True, True)
    
    inputStartPos = lcd.cursorPos[0]
    
    exit = False
    old = None
    password = []
    
    while (not exit):
        val = pad.scan()
        
        if val != old:
            old = val
            
            if val != None:
                if isNumber(val):
                    lcd.print(val)
                    password.append(val)
                elif val == 'C':
                    if(lcd.cursorPos[0] > inputStartPos):
                        lcd.shift(-1)
                        lcd.print(" ", updateCursorPos = False)
                        lcd.shift(-1)
                        password.pop(-1)
                elif val == 'D':
                    
                    if(len(password) == 0):
                        lcd.printLine("Proceed with no\npword?  1=Y  0=N")
                        ##GET ONE KEYPRESS
                        sleep(1500) #actually wait for user confirmation
                        lcd.printLine("You can always\nset one later on") #if YES
                    else:
                        lcd.printLine("Confirm " + str("".join(password)) + "\n" + "1=Yes  0=No")
                        lcd.moveCursor(lcd.nCols-1, lcd.nRows-1)
                        ##GET ONE KEYPRESS
        
        sleep(120)

def isNumber(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
        