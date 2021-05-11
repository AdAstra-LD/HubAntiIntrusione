import memory.customflash as flash
import memory.memorymap as memmap
import userinput.keypad as pad

SYSTEM_UNINITIALIZED = 0
SYSTEM_UNPROTECTED = 1
SYSTEM_PROTECTED = 1

PASSWORD_MAXLEN = 8

def userSetup(lcd, pad):
    flashmem = flash.FlashFileStream(memmap.ESP32_BASEADDR, 9)
    flashmem[0] = SYSTEM_UNINITIALIZED  #PER FARE IN MODO CHE LA PASSWORD SIA SEMPRE CHIESTA
    
    lcd.printLine("Unisa - IOT 2021\nLaiso, Macaro", align = "C")
    sleep(500)
    systemStatus = flashmem.read_byte()
    
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
    lcd.cursorConfig(True, True, True) #Imposta il cursore lampeggiante
    
    inputStartPos = lcd.cursorPos[0] #Memorizza la posizione iniziale di inserimento
    password = []                       #crea una lista vuota per contenere la password
    
    while (True):
        val = pad.scan()
        posInPassword = lcd.cursorPos[0] - inputStartPos
        
        if isNumber(val):
            if len(password) < PASSWORD_MAXLEN:
                print("pos in password: " + str(posInPassword) + "  pw len: " + str(len(password)))
                if posInPassword > len(password)-1:
                    password.append(val)
                else:
                    password[posInPassword] = val
                    
                lcd.print(val)
            print("La password attuale e': " + str(password))
        elif val == 'D':
            if len(password) == 0:
                lcd.printLine("Proceed with no\npword?  1=Y  0=N")
                ##GET ONE KEYPRESS
                sleep(1500) #actually wait for user confirmation
                lcd.printLine("You can always\nset one later on") #if YES
                lcd.cursorConfig(True, False, False)
            else:
                lcd.printLine("Confirm " + str("".join(password)) + "\n" + "1=Yes  0=No")
                lcd.moveCursor(lcd.nCols-1, lcd.nRows-1)
                ##GET ONE KEYPRESS
        elif val == 'C':
            if posInPassword > 0:
                lcd.shift(-1)
                password.pop(posInPassword - 1)
                whitespaces = ' ' * (PASSWORD_MAXLEN-len(password))
                remaining = password[posInPassword-1:]
                
                x = lcd.cursorPos[0]
                lcd.print(str("".join(remaining) + whitespaces))
                lcd.moveCursor(x, lcd.cursorPos[1])
        elif val == '*':
            if(posInPassword > 0):
                lcd.shift(-1) #shift sinistra 
        elif val == '#':
            if(posInPassword < len(password)):
                lcd.shift(1) #shift destra 
            

def isNumber(s):
    try:
        int(s)
        return True
    except ValueError:
        return False