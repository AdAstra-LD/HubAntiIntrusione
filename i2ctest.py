# I2C Test
# Created at 2021-04-25 15:31:22.217931

#In caso di eccezione AttributeError, ricontrollare il nome della funzione chiamata

import i2clcd
import streams

clk = 9600
streams.serial(baud = clk)


print("Initializing...")
lcd = i2clcd.I2CLCD(I2Cport = I2C0, baud = 100000, i2c_addr=0x27, lcd_width=16)
lcd.prepare()
#lcd.print('Salve, gente')
specialChar0 = (0x15, 0x00, 0x15, 0x00, 0x15, 0x00, 0x15, 0x00)
specialChar1 = (0x00, 0x15, 0x00, 0x15, 0x00, 0x15, 0x00, 0x15)
tridente = (0x15, 0x15, 0x15, 31, 4, 4, 4, 4)
lcd.writeCGRAM(specialChar0, 0)
lcd.writeCGRAM(specialChar1, 1)
lcd.writeCGRAM(tridente, 2)
lcd.moveCursor(0, 0) #riga, colonna
lcd.printLine("C0 " + i2clcd.CGRAM_CHAR[0] + " C1 " + i2clcd.CGRAM_CHAR[1] + "New: " + i2clcd.CGRAM_CHAR[2], 1, "RIGHT")

digitalWrite(pinLed, LOW)

lcd.setCursor(1, 1) #prepare
lcd.setCursor(2, 2) #activate cursor and blink
