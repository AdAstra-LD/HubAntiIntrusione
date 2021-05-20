# Test Infrared Sensor
# Created at 2021-04-22 16:04:22.591934

import streams
import threading

import adc
import pwm
import i2c

import display.LCDI2C as lcdi2c
import display.specialChars as chars
import display.localDashboard as ui
import userinput.settings as settings
import userinput.keypad as keypad
import communication.comm as comm

pinAlarmLed = D5    
pinEnableLed = D23

pinBuzzer = D15.PWM
pinPhotoresist = A2

pinIR = D22
pinEnButton = D21

initialFreq = 150;
abilitato = False;
audioEnable = True;
flashEnable = True;

global lcd

def readAmbientLight():
    while True:
        valore = 4096-adc.read(pinPhotoresist)
        string = str(round(100*valore/4095)) + "%  "
        
        lcd.returnHome()
        lcd.print(string)
        sleep(300)

def initIO():
    streams.serial(baud = 100000)
    
    global lcd
    lcd = initLCD(I2C2)
    
    keypadPinSetup = (A0, A1, D25, D26, D27, D14, D12, D13)
    pad = keypad.KeyPad(keypadPinSetup)
    settings.userSetup(lcd, pad)
    
    print("Setting up output pins...")
    pinMode(pinAlarmLed, OUTPUT)
    pinMode(pinEnableLed, OUTPUT)
    pinMode(pinBuzzer, OUTPUT)
    
    print("Setting up input pins...")
    pinMode(pinPhotoresist, INPUT)
    pinMode(pinIR, INPUT)
    pinMode(pinEnButton, INPUT_PULLDOWN)
    
    print("Turning LEDs off...")
    digitalWrite(pinEnableLed, LOW)
    digitalWrite(pinAlarmLed, LOW)
    
    #comm.AlarmComm("FASTWEB-RML2.4", "marcheselaiso@2020 2.4")
    #comm.runThreadedTask(readAmbientLight)

def toggleOnOff():
    global audioEnable
    global flashEnable
    
    pinToggle(pinEnableLed)
    status = abilitato
    abilitato = not status
    audioEnable = not status
    flashEnable = not status
    
    lcd.clear()

    if (abilitato):
        lcd.printAtPos(lcd.CGRAM[4], lcd.nCols-1, 0) #EXCLAMATION
        print("Sistema abilitato")
    else:
        stopAlarm()
        lcd.printAtPos(' ', lcd.nCols-1, 0)
        print("Sistema disabilitato")

def intrusione():
    global audioEnable
    global flashEnable
    
    if (abilitato):
        print("Intrusione!!!")
        audioEnable = True
        flashEnable = True
        thread(soundAlarm)
        thread(flashLed, pinAlarmLed, 25)
        lcd.printLine("!  Intruder  !", 1, align = "CENTER")
    else:
        print("Movimento rilevato... ma l'allarme non e' inserito")

def stopAlarm():
    global audioEnable
    global flashEnable
    
    print("Stopping alarm...")
    audioEnable = False
    flashEnable = False
    
    pwm.write(pinBuzzer, 0, 0)
    digitalWrite(pinAlarmLed, LOW)

def soundAlarm(initialFreq = 2350, finalFreq = 200, increment = -12, delay = 2):
    global audioEnable
    
    if initialFreq == 0 or delay == 0 or increment == 0:
        return
        
    currentFreq = initialFreq
    
    while (audioEnable):
        #we are using MICROS so every sec is 1000000 of micros. 
        #// is the int division, pwm.write period doesn't accept floats
        period=1000000//currentFreq
        
        #set the period of the buzzer and the duty to 50% of the period
        pwm.write(pinBuzzer, period, period//2, MICROS)
        
        # increment the frequency every loop
        currentFreq = currentFreq + increment 
        
        # reset period
        if abs(currentFreq - finalFreq) < abs(increment):
            currentFreq = initialFreq
            print("ping")
            
        sleep(delay)

def flashLed(led, flashFrequency):
    global flashEnable
    
    if (flashFrequency == 0):
        flashFrequency = 1
        
    while (flashEnable):
        pinToggle(led)
        sleep(1000//flashFrequency)
        
def initLCD(port = I2C0):
    lcdObj = lcdi2c.LCDI2C(port, nCols=16, nRows=2)
    if (port == None):
        return lcdObj
    
    lcdObj.prepare()
    lcdObj.writeCGRAM(chars.TEMPERATURE, 0)
    lcdObj.writeCGRAM(chars.HUMIDITY, 1)
    lcdObj.writeCGRAM(chars.LIGHT, 2)
    lcdObj.writeCGRAM(chars.CELSIUS, 3)
    lcdObj.writeCGRAM(chars.EXCLAMATION, 4)
    lcdObj.writeCGRAM(chars.UNLOCKED, 5)
    lcdObj.writeCGRAM(chars.WIFI, 6)
    #lcdObj.writeCGRAM(chars.LOCKED, 7) #this acts as a temp buffer
    
    return lcdObj


initIO()
onPinRise(pinEnButton, toggleOnOff)
onPinRise(pinIR, intrusione)
onPinFall(pinIR, stopAlarm)
