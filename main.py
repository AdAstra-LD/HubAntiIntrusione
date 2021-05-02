# Test Infrared Sensor
# Created at 2021-04-22 16:04:22.591934

import streams
import threading

import adc
import pwm
import i2c
import src.i2clcd as display
import src.specialChars as chars

pinAlarmLed = D0    
pinEnableLed = D15
pinBuzzer = D13.PWM

pinIR = A1
pinEnButton = D12


initialFreq = 150;
abilitato = False;
audioEnable = True;
flashEnable = True;

def initIO():
    global lcd
    streams.serial(baud = 100000)
    
    lcd = display.I2CLCD(I2C2, lcd_cols=16, lcd_rows=2)
    lcd.prepare()
    
    pinMode(pinAlarmLed, OUTPUT)
    pinMode(pinEnableLed, OUTPUT)
    pinMode(pinBuzzer, OUTPUT)
    
    pinMode(pinIR, INPUT)
    pinMode(pinEnButton, INPUT_PULLDOWN)
    
    digitalWrite(pinEnableLed, LOW)
    digitalWrite(pinAlarmLed, LOW)
    
    lcd.writeCGRAM(chars.SMILEY_FACE, 0)
    lcd.writeCGRAM(chars.SAD_FACE, 1)
    lcd.writeCGRAM(chars.POKER_FACE, 2)
    lcd.writeCGRAM(chars.BIG_EXCLAMATION, 3)
    
    print("Sistema pronto.")

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
        lcd.printAtPos(display.CGRAM_CHAR[3], lcd.nCols-1, 0)
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
    global flashEnable;
    
    if (flashFrequency == 0):
        flashFrequency = 1
        
    while (flashEnable):
        pinToggle(led)
        sleep(1000//flashFrequency)

initIO()
onPinRise(pinEnButton, toggleOnOff)
onPinRise(pinIR, intrusione)
onPinFall(pinIR, stopAlarm)
