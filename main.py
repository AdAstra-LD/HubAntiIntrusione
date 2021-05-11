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

pinAlarmLed = A0    
pinEnableLed = A1
pinBuzzer = D13.PWM
pinPhotoresist = A4

pinIR = A7
pinEnButton = D9

initialFreq = 150;
abilitato = False;
audioEnable = True;
flashEnable = True;

def initIO():
    streams.serial(baud = 100000)
    
    global lcd
    lcd = initLCD(I2C0)
    pad = keypad.KeyPad(keypad.PINSETUP_GPIOEXT_D15__D05)
    settings.userSetup(lcd, pad)
    
    print("Setting up pins...")
    pinMode(pinAlarmLed, OUTPUT)
    pinMode(pinEnableLed, OUTPUT)
    pinMode(pinBuzzer, OUTPUT)
    pinMode(pinPhotoresist, INPUT)
    
    pinMode(pinIR, INPUT)
    pinMode(pinEnButton, INPUT_PULLDOWN)
    
    print("Turning LEDs off...")
    digitalWrite(pinEnableLed, LOW)
    digitalWrite(pinAlarmLed, LOW)
    
    #while True:
    #    pl = 4095-adc.read(pinPhotoresist)
    #    print(str(100*pl//4095) + "%")
    #    sleep(500)

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
        lcd.printAtPos(lcdi2c.CGRAM_CHAR[1], lcd.nCols-1, 0) #EXCLAMATION
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
    lcdObj = lcdi2c.LCDI2C(port, lcd_cols=16, lcd_rows=2)
    if (port == None):
        return lcdObj
    
    lcdObj.prepare()
    lcdObj.writeCGRAM(chars.SMILEY_FACE, 0)
    lcdObj.writeCGRAM(chars.BIG_EXCLAMATION, 1)
    lcdObj.writeCGRAM(chars.TEMPERATURE, 2)
    lcdObj.writeCGRAM(chars.HUMIDITY, 3)
    lcdObj.writeCGRAM(chars.LIGHT, 4)
    lcdObj.writeCGRAM(chars.CELSIUS, 5)
    
    return lcdObj

initIO()
onPinRise(pinEnButton, toggleOnOff)
onPinRise(pinIR, intrusione)
onPinFall(pinIR, stopAlarm)
