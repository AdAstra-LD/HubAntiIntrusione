import peripherals.keypad as pad
import peripherals.specialChars as chars

import memory.custom_flash as flash
import utilities.cMath as cMath
import utilities.music as music

###MEMORY MAP###
ESP32_BASEADDR = 0x00310000

SETUP_INFO_OFFSET = 0
PASSWORD_LENGTH_OFFSET = 1
USER_PASSWORD_OFFSET = 2

SETUP_INFO_ADDR = ESP32_BASEADDR + SETUP_INFO_OFFSET
PASSWORD_LENGTH_ADDR = ESP32_BASEADDR + PASSWORD_LENGTH_OFFSET 
USER_PASSWORD_ADDR = ESP32_BASEADDR + USER_PASSWORD_OFFSET

SYSTEM_UNINITIALIZED = 0
SYSTEM_UNPROTECTED = 1
SYSTEM_PROTECTED = 2
################

class UserSettings():
    def __init__(self, lcd, keypad, ledRGB, buzz, pwMaxLen = 8):
        self.lcd = lcd
        self.keypad = keypad
        self.ledRGB = ledRGB
        self.buzzer = buzz
        
        self.PASSWORD_MAXLEN = min(8, pwMaxLen)
        self.flash_size = USER_PASSWORD_OFFSET + self.PASSWORD_MAXLEN
        self.flashMem = flash.FlashFileStream(ESP32_BASEADDR, self.flash_size)
        self.systemStatus = self.flashMem[SETUP_INFO_OFFSET]
        self.pw = self.readPw()
        
        ############################################
        #print(str(self.flashMem[SETUP_INFO_OFFSET]))
        
        if self.systemStatus != SYSTEM_UNPROTECTED and self.systemStatus != SYSTEM_PROTECTED:
            self.systemStatus = SYSTEM_UNINITIALIZED
            self.userSetup()
        #else: #debug purposes only
        #    for x in range(self.flash_size):
        #        print(str(x) + ' ' + str(self.flashMem[x]))
    
    def readPw(self):
        self.pw = []
        if self.systemStatus == SYSTEM_PROTECTED:
            pwLen = self.flashMem[PASSWORD_LENGTH_OFFSET]
            
            self.flashMem.move_cursor(USER_PASSWORD_OFFSET)
            return self.flashMem.read_bytes(pwLen)
        
    
    def userSetup(self):
        self.lcd.writeCGRAM(chars.SMILEY_FACE, 7) #Temp buffer --> #SmileyFace
        self.lcd.printLine("Welcome! " + self.lcd.CGRAM[7], delay = 20, align = "C")
        self.buzzer.playSequence(music.welcomeTone, BPM = 265)
        sleep(1500)
        
        self.lcd.printLine("There are a few\nthings to set up")
        sleep(1500)
        
        self.lcd.printLine("Please choose a\npassword for the\nalarm system.")
        sleep(1500)
        
        self.pw = self.passwordScreen()
        pwlen = len(self.pw)
        #print("user chose password: " + str(self.pw))
        #print("its length is: " + str(pwlen))
        
        if pwlen > 0:         
            self.systemStatus = SYSTEM_PROTECTED
        else:
            self.systemStatus = SYSTEM_UNPROTECTED
            self.lcd.printLine("You can always\nset one later.")
        
        self.flashMem[SETUP_INFO_OFFSET] = self.systemStatus
        self.flashMem[PASSWORD_LENGTH_OFFSET] = pwlen
        for x in range(pwlen):  
            self.flashMem[USER_PASSWORD_OFFSET+x] = int(self.pw[x])
    
        self.flashMem.flush()
        sleep(500)
        print("PW written to memory.")
    
    def resetAll(self):
        self.lcd.printLine("Hard reset?", delay = 100)
        self.lcd.print("1=Y  0=N", row = 1, align = 'RIGHT')
        val = self.keypad.scan(('1', '0'))
                    
        if val == '1':
            self.ledRGB.RGBset(255, 255, 0)
            self.lcd.printLine("Absolutely sure?", delay = 100)
            self.buzzer.playSequence(music.warningTone, BPM = 140, duty = 50)
            sleep(500)
            self.lcd.print("0=Y  1=N", row = 1, align = 'RIGHT')
            self.ledRGB.quickBlink(R=255, G=0, B=0)
            self.ledRGB.RGBset(255, 0, 0)
            
            val = self.keypad.scan(('1', '0'))
            
            if val == '0':
                self.ledRGB.RGBset(255, 255, 255)
                self.flashMem.erase(0, self.flash_size, immediate = True)
                
                self.lcd.printLine("Confirmed.", delay = 50)
                self.ledRGB.quickBlink(colorTuple = (0, 255, 0))
                self.ledRGB.RGBset(colorTuple = (0, 255, 0))
                self.buzzer.playSequence(music.successTone, BPM = 210, duty = 50)
                sleep(500)
                self.lcd.printLine("Please restart\nthe alarm system")
                
                while True:
                    sleep(10000)
        
        self.lcd.printLine("Discarded.", delay = 0)
        sleep(1500)
        return


    def passwordScreen(self, toCompare = [], discardable = True):
        while True:
            temp_pw = []                       #inizializza lista vuota per contenere la temp_pw
            self.lcd.returnHome()
            self.lcd.printLine("B=Backsp  D=Done", row = 1)
            self.lcd.returnHome()
            self.lcd.print("  PW: ")
            self.lcd.cursorConfig(True, True, True) #Imposta il cursore lampeggiante)
        
            inputStartPos = self.lcd.cursorPos[0]    #Memorizza la posizione iniziale di inserimento
            val = ''                            #BUFFER ultimo tasto premuto
            self.lcd.flashDisplay(2, 150)
            
            while val != 'D':
                val = self.keypad.scan()
                posInTemp_pw = self.lcd.cursorPos[0] - inputStartPos
                curlen = len(temp_pw)
                
                if cMath.isNumber(val):
                    print("pos in temp_pw: " + str(posInTemp_pw) + "  self.pw len: " + str(len(temp_pw)))
                    if posInTemp_pw < curlen: #Se posizione del cursore non è sull'ultimo char
                        temp_pw[posInTemp_pw] = val #sostituzione
                        self.lcd.print(val)
                    elif curlen < self.PASSWORD_MAXLEN: #Altrimenti assicurati di poter aggiungere
                        temp_pw.append(val)
                        self.lcd.print(val)
                    else:
                        self.ledRGB.quickBlink(R=255)
                        self.buzzer.playSequence(music.waitTone, BPM = 240)
                elif val == 'B':
                    if posInTemp_pw > 0:
                        self.lcd.shift(-1)
                        temp_pw.pop(posInTemp_pw - 1)
                        whitespaces = ' ' * (self.PASSWORD_MAXLEN-len(temp_pw))
                        remaining = temp_pw[posInTemp_pw-1:]
                        
                        x = self.lcd.cursorPos[0]
                        self.lcd.print(str("".join(remaining) + whitespaces))
                        self.lcd.moveCursor(x, self.lcd.cursorPos[1])
                elif val == '*':
                    if(posInTemp_pw > 0):
                        self.lcd.shift(-1) #shift sinistra 
                elif val == '#':
                    if(posInTemp_pw < len(temp_pw)):
                        self.lcd.shift(1) #shift destra 
            #}
            
            self.lcd.cursorConfig(True, False, False)            
            if len(temp_pw) == 0:
                if discardable and toCompare == []:
                    self.lcd.printLine("Proceed with no\npword?")
                    self.lcd.print("1=Y  0=N", row = 1, align = 'RIGHT')
                    
                    val = self.keypad.scan(('1', '0'))
                    
                    if val == '1':
                        self.ledRGB.RGBset(0, 255, 0)
                        self.lcd.printLine("Confirmed.")
                        self.buzzer.playSequence(music.successTone, BPM = 210, duty = 50)
                        self.ledRGB.quickBlink(G=255)
                        sleep(400)
                        self.lcd.clear()
                        
                        return temp_pw
                    else:
                        print("Retrying...")
                        temp_pw = []
                elif discardable and toCompare != []:
                    self.lcd.printLine("Discard?")
                    self.lcd.print("1=Y  0=N", row = 1, align = 'RIGHT')
                    
                    val = self.keypad.scan(('1', '0'))
                    
                    if val == '1':
                        self.lcd.clear()
                        return False
                    else:
                        print("Retrying...")
                        temp_pw = []
                else:
                    self.ledRGB.quickBlink(R=255)
                    self.buzzer.playSequence(music.waitTone, BPM = 240)
            else:
                self.lcd.printLine("Confirm " + str("".join(temp_pw)))
                self.lcd.print("1=Yes  0=Retry", row = 1, align = 'RIGHT')
                
                self.lcd.moveCursor(self.lcd.nCols-1, self.lcd.nRows-1)
                val = self.keypad.scan(('1', '0'))
                
                if val == '1':
                    if toCompare == []:
                        self.ledRGB.RGBset(0, 255, 0)
                        self.lcd.printLine("Pword confirmed.")
                        self.buzzer.playSequence(music.successTone, BPM = 210, duty = 50)
                        self.ledRGB.quickBlink(G=255)
                        sleep(400)
                        self.lcd.clear()
                        
                        return temp_pw
                    elif str(temp_pw) == str(toCompare):#self.listEqual(temp_pw, toCompare):
                        self.ledRGB.RGBset(0, 255, 0)
                        self.lcd.printLine("Pword accepted.")
                        sleep(400)
                        self.lcd.clear()
                        return True
                    else:
                        self.ledRGB.quickBlink(R=255)
                        self.buzzer.playSequence(music.waitTone, BPM = 240)
                else:
                    print("Retrying...")
        #}
        print("Setup completed")
        
    #def listEqual(self, l1, l2):
    #    len1 = len(l1)
    #    len2 = len(l2)
    #    
    #    print ("len1" + str(len1) + ", len2" + str(len2))
    #    if len1 != len(l2):
    #        return False
    #    for x in range(len1):
    #        print(str(l1[x]) + " and " + str(l2[x]))
    #        if l1[x] != l2[x]:
    #            print("exiting")
    #            return False
    #            
    #    return True