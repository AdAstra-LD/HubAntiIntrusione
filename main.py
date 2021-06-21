# Test Infrared Sensor
# Created at 2021-04-22 16:04:22.591934

import streams
import threading

import pwm
import i2c

import display.LCDI2C as lcdi2c
import display.specialChars as chars
import display.localDashboard as ui
import userinput.settings as settings
import userinput.keypad as keypad
import communication.comm as comm
import led
import glob

pinBuzzer = D15.PWM
#pinPhotoresist = A2

pinIR = D5
pinEnButton = D21
#pinSettingsButton = D2

def readAmbientLight():
    while True:
        valore = 4096-adc.read(pinPhotoresist)
        string = str(round(100*valore/4095)) + "%  "
        
        glob.lcd.returnHome()
        glob.lcd.print(string)
        sleep(300)

def initIO():
    streams.serial()
    
    glob.lcd = initLCD(I2C2)
    
    glob.pad = keypad.KeyPad(invert = True)
    
    print("Setting up LED...")
    glob.setupRGBled(D4, D22, D23) #R, G, B
    led.RGBoff()
    
    print("Setting up buzzer...")
    pinMode(pinBuzzer, OUTPUT)
    
    print("Setting up input pins...")
    pinMode(pinIR, INPUT)
    #pinMode(pinPhotoresist, INPUT)
    #pinMode(pinSettingsButton, INPUT_PULLDOWN)
    pinMode(pinEnButton, INPUT_PULLUP)
    
    sleep(750)
    print("Setup completed")
    settings.load()
    
    #comm.AlarmComm("FASTWEB-RML2.4", "marcheselaiso@2020 2.4")
    #comm.runThreadedTask(readAmbientLight)

def toggleOnOff():
    status = glob.alarmEnable
    glob.alarmEnable = not status
    glob.audioEnable = not status
    glob.flashEnable = not status

    if (glob.alarmEnable):
        led.RGBset(0, 0, 1)
        print("Sistema abilitato")
    else:
        led.memorizeColor(0, 0, 0)
        led.RGBoff()
        stopAlarm()
        print("Sistema disabilitato")

def intrusione():
    if (glob.alarmEnable):
        led.flash(glob.pinTuple[0], 20)
        thread(soundAlarm)
        print("Intrusione!!!")
    else:
        print("Movimento rilevato... ma l'allarme non e' inserito")

def stopAlarm():
    print("Alarm signal down...")
    glob.audioEnable = False
    glob.flashEnable = False
    
    pwm.write(pinBuzzer, 0, 0)
    led.RGBset(R = 0)

def soundAlarm(initialFreq = 2350, finalFreq = 200, increment = -12, delay = 2):
    if initialFreq == 0 or initialFreq < finalFreq or delay == 0 or increment == 0:
        return
        
    glob.audioEnable = True
    currentFreq = initialFreq
    
    while (glob.audioEnable):
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
#PINS MUST BE ALREADY INITIALIZED, BEFORE THESE INTERRUPTS ARE SET UP
onPinFall(pinEnButton, toggleOnOff)
#onPinRise(pinSettingsButton, settings.userSetup)
onPinRise(pinIR, intrusione)
onPinFall(pinIR, stopAlarm)
