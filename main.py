# Test Infrared Sensor
# Created at 2021-04-22 16:04:22.591934

import streams
import threading

import adc
import pwm
import i2c
import i2clcd as display
import specialChars as chars

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
    
    i2cObj = i2c.I2C(I2C2, addr=0x27, clock=100000)
    i2cObj.start()
    
    lcd = display.I2CLCD(i2cObj, lcd_cols=16, lcd_rows=2)
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
    sleep(1250)
    lcd.printLine("Hai proprio l'", 0, align = "L", delay = 60)
    lcd.printLine("aria di uno che", 1, align = "L", delay = 60)
    sleep(400)
    lcd.clear()
    
    lcd.printLine("si chiama", 0, align = "L", delay = 60)
    lcd.printLine("Alessandro", 1, align = "L", delay = 60)
    
    print(lcd.cursorPos)
    
    lcd.shift()
    
    print(lcd.cursorPos)
    
    lcd.print(display.CGRAM_CHAR[2])
    sleep(1250)
    lcd.clear()
    lcd.printLine("Wa, non ci credo Ho indovinato?", 0, align = "L", delay = 60)
    
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
        lcd.printAt(lcd.nCols-1, 0, display.CGRAM_CHAR[3])
        print("Sistema abilitato")
    else:
        stopAlarm()
        lcd.printAt(lcd.nCols-1, 0, ' ')
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
    
    if (initialFreq == 0 or delay == 0 or increment == 0):
        return
        
    currentFreq = initialFreq
    
    while (audioEnable):
        period=1000000//currentFreq #we are using MICROS so every sec is 1000000 of micros. // is the int division, pwm.write period doesn't accept floats
        
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
