import peripherals.keypad as pad
import peripherals.specialChars as chars

import memory.customflash as flash
import memory.memorymap as memmap
import utilities.cMath as cMath
import utilities.music as music

SYSTEM_UNINITIALIZED = 0
SYSTEM_UNPROTECTED = 1
SYSTEM_PROTECTED = 2

class UserSettings():
    def __init__(self, lcd, keypad, ledRGB, buzz, pwMaxLen = 8):
        self.PASSWORD_MAXLEN = min(8, pwMaxLen)
        self.flash_size = memmap.USER_PASSWORD_OFFSET + self.PASSWORD_MAXLEN
        self.lcd = lcd
        self.keypad = keypad
        self.ledRGB = ledRGB
        self.buzzer = buzz
        self.flashMem = flash.FlashFileStream(memmap.ESP32_BASEADDR, self.flash_size)
        
        print(str(self.flashMem[memmap.SETUP_INFO_OFFSET]))
        systemStatus = self.flashMem[memmap.SETUP_INFO_OFFSET]
        
        if systemStatus != SYSTEM_UNPROTECTED and systemStatus != SYSTEM_PROTECTED:
            systemStatus = SYSTEM_UNINITIALIZED
            self.userSetup()
        else: #debug purposes only
            for x in range(self.flash_size):
                print(str(x) + ' ' + str(self.flashMem[x]))
    
    def userSetup(self):
        self.lcd.clear()
        
        self.lcd.writeCGRAM(chars.SMILEY_FACE, 7) #Temp buffer --> #SmileyFace
        self.lcd.printLine("Welcome! " + self.lcd.CGRAM[7], delay = 20, align = "C")
        self.buzzer.playSequence(music.welcomeTone, BPM = 265)
        sleep(1500)
        
        self.lcd.printLine("There are a few\nthings to set up")
        sleep(1500)
        
        self.lcd.printLine("Please choose a\npassword for the\nalarm system.")
        sleep(1500)
        
        pw = self.passwordScreen()
        if len(pw) > 0:         
            self.flashMem[memmap.SETUP_INFO_OFFSET] = SYSTEM_PROTECTED
        else:
            self.flashMem[memmap.SETUP_INFO_OFFSET] = SYSTEM_UNPROTECTED
            self.lcd.printLine("You can always\nset one later.")
        
        for x in range(len(pw)):
            self.flashMem[memmap.USER_PASSWORD_OFFSET+x] = int(pw[x])
    
        self.flashMem.flush()
        print("PW written to memory.")
        
    def passwordScreen(self):
        password = []                       #inizializza lista vuota per contenere la password
        selectionConfirmed = False          #variabile che consente di uscire dalla schermata di selezione
        
        while (not selectionConfirmed):
            self.lcd.returnHome()
            self.lcd.printLine("B=Backsp  D=Done", row = 1)
            self.lcd.returnHome()
            self.lcd.print("  PW: ")
            self.lcd.cursorConfig(True, True, True) #Imposta il cursore lampeggiante
            self.lcd.flashDisplay(2, 70)
        
            inputStartPos = self.lcd.cursorPos[0]    #Memorizza la posizione iniziale di inserimento
            val = ''                            #BUFFER ultimo tasto premuto
        
            while(val != 'D'):
                val = self.keypad.scan()
                posInPassword = self.lcd.cursorPos[0] - inputStartPos
                curlen = len(password)
                
                if cMath.isNumber(val):
                    print("pos in password: " + str(posInPassword) + "  pw len: " + str(len(password)))
                    if posInPassword < curlen: #Se posizione del cursore non è sull'ultimo char
                        password[posInPassword] = val #sostituzione
                        self.lcd.print(val)
                    elif curlen < self.PASSWORD_MAXLEN: #Altrimenti assicurati di poter aggiungere
                        password.append(val)
                        self.lcd.print(val)
                    else:
                        self.ledRGB.quickBlink(R=1)
                        self.buzzer.playSequence(music.waitTone, BPM = 240)
                elif val == 'B':
                    if posInPassword > 0:
                        self.lcd.shift(-1)
                        password.pop(posInPassword - 1)
                        whitespaces = ' ' * (self.PASSWORD_MAXLEN-len(password))
                        remaining = password[posInPassword-1:]
                        
                        x = self.lcd.cursorPos[0]
                        self.lcd.print(str("".join(remaining) + whitespaces))
                        self.lcd.moveCursor(x, self.lcd.cursorPos[1])
                elif val == '*':
                    if(posInPassword > 0):
                        self.lcd.shift(-1) #shift sinistra 
                elif val == '#':
                    if(posInPassword < len(password)):
                        self.lcd.shift(1) #shift destra 
            #}
            
            self.lcd.cursorConfig(True, False, False)            
            if len(password) == 0:
                self.lcd.printLine("Proceed with no\npword?  1=Y  0=N")
                
                val = self.keypad.scan(('1', '0'))
                
                if (val == '1'):
                    self.lcd.printLine("Confirmed.")
                    self.buzzer.playSequence(music.successTone, BPM = 210, duty = 50)
                    sleep(1000)
                    
                    selectionConfirmed = True
                    return password
                else:
                    print("Retrying...")
                    password = []
            else:
                self.lcd.printLine("Confirm " + str("".join(password)) + "\n" + "1=Yes  0=Retry")
                self.lcd.moveCursor(self.lcd.nCols-1, self.lcd.nRows-1)
                val = self.keypad.scan(('1', '0'))
                
                if (val == '1'):
                    self.lcd.printLine("Pword confirmed.")
                    self.buzzer.playSequence(music.successTone, BPM = 210, duty = 50)
                    sleep(1000)
                    
                    selectionConfirmed = True
                    return password
                else:
                    print("Retrying...")
                    password = []
        #}
        print("Setup completed")
        