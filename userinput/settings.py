import memory.customflash as flash
import memory.memorymap as memmap
import userinput.keypad as pad
import display.specialChars as chars
import glob

SYSTEM_UNINITIALIZED = 0
SYSTEM_UNPROTECTED = 1
SYSTEM_PROTECTED = 2

PASSWORD_MAXLEN = 8
FLASH_SIZE = memmap.USER_PASSWORD_OFFSET + PASSWORD_MAXLEN

flashMem = flash.FlashFileStream(memmap.ESP32_BASEADDR, FLASH_SIZE)
password = []

def load():
    print(str(flashMem[memmap.SETUP_INFO_OFFSET]))
    status = flashMem[memmap.SETUP_INFO_OFFSET]
    
    if status != SYSTEM_UNPROTECTED and status != SYSTEM_PROTECTED:
        status = SYSTEM_UNINITIALIZED
        userSetup()
    else:
        for x in range(FLASH_SIZE):
            print(str(x) + ' ' + str(flashMem[x]))

def userSetup():
    glob.lcd.clear()
    
    glob.lcd.printLine("Welcome!", align = "C")
    glob.lcd.shift()
    
    glob.lcd.writeCGRAM(chars.SMILEY_FACE, 7) 
    glob.lcd.print(glob.lcd.CGRAM[7]) #SmileyFace
    sleep(1500)
    
    glob.lcd.printLine("There are a few\nthings to set up")
    sleep(1500)
    
    glob.lcd.printLine("Please choose a\npassword for the\nalarm system.")
    sleep(1500)
    
    pw = passwordScreen()
    flashMem[memmap.SETUP_INFO_OFFSET] = SYSTEM_PROTECTED
    flashMem[memmap.PASSWORD_LENGTH_OFFSET] = len(pw)
    
    for x in range(len(pw)):
        flashMem[memmap.USER_PASSWORD_OFFSET+x] = int(pw[x])

    flashMem.flush()
    print("PW written to RAM...")
    
def passwordScreen():
    password = []                       #inizializza lista vuota per contenere la password
    selectionConfirmed = False          #variabile che consente di uscire dalla schermata di selezione
    
    while (not selectionConfirmed):
        glob.lcd.returnHome()
        glob.lcd.printLine("B=Backsp  D=Done", row = 1)
        glob.lcd.returnHome()
        glob.lcd.print("  PW: ")
        glob.lcd.cursorConfig(True, True, True) #Imposta il cursore lampeggiante
    
        inputStartPos = glob.lcd.cursorPos[0]    #Memorizza la posizione iniziale di inserimento
        val = ''                            #BUFFER ultimo tasto premuto
    
        while(val != 'D'):
            val = glob.pad.scan()
            posInPassword = glob.lcd.cursorPos[0] - inputStartPos
            curlen = len(password)
            
            if glob.isNumber(val):
                print("pos in password: " + str(posInPassword) + "  pw len: " + str(len(password)))
                if posInPassword < curlen: #Se posizione del cursore non è sull'ultimo char
                    password[posInPassword] = val #sostituzione
                    glob.lcd.print(val)
                elif curlen < PASSWORD_MAXLEN: #Altrimenti assicurati di poter aggiungere
                    password.append(val)
                    glob.lcd.print(val)
                else:
                    glob.ledRGB.quickBlink(R=1)
            elif val == 'B':
                if posInPassword > 0:
                    glob.lcd.shift(-1)
                    password.pop(posInPassword - 1)
                    whitespaces = ' ' * (PASSWORD_MAXLEN-len(password))
                    remaining = password[posInPassword-1:]
                    
                    x = glob.lcd.cursorPos[0]
                    glob.lcd.print(str("".join(remaining) + whitespaces))
                    glob.lcd.moveCursor(x, glob.lcd.cursorPos[1])
            elif val == '*':
                if(posInPassword > 0):
                    glob.lcd.shift(-1) #shift sinistra 
            elif val == '#':
                if(posInPassword < len(password)):
                    glob.lcd.shift(1) #shift destra 
        #}
        
        glob.lcd.cursorConfig(True, False, False)            
        if len(password) == 0:
            glob.lcd.printLine("Proceed with no\npword?  1=Y  0=N")
            
            val = glob.pad.scan(('1', '0'))
            
            if (val == '1'):
                glob.lcd.printLine("You can always\nset one later.") #if YES
                
                flashMem[memmap.SETUP_INFO_OFFSET] = SYSTEM_UNPROTECTED
                flashMem[memmap.PASSWORD_LENGTH_OFFSET] = 0
                for x in range(PASSWORD_MAXLEN):
                    flashMem[memmap.USER_PASSWORD_OFFSET+x] = 0
                
                print("Settings written to RAM...")
                selectionConfirmed = True
            else:
                print("Retrying...")
                password = []
        else:
            glob.lcd.printLine("Confirm " + str("".join(password)) + "\n" + "1=Yes  0=Retry")
            glob.lcd.moveCursor(glob.lcd.nCols-1, glob.lcd.nRows-1)
            val = glob.pad.scan(('1', '0'))
            
            if (val == '1'):
                glob.lcd.printLine("Pword confirmed.")
                    
                selectionConfirmed = True
                return password
            else:
                print("Retrying...")
                password = []
    #}
    print("Setup completed")
    