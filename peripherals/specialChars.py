all = 0b11111
nul = 0

#Communication
SMILEY_FACE =       (nul, 0b01010, 0b01010, nul, 0b10001, 0b01110, nul, nul)
SAD_FACE =          (nul, 0b01010, 0b01010, nul, 0b01110, 0b10001, nul, nul)
POKER_FACE =        (nul, 0b01010, 0b01010, nul, all, nul, nul, nul)
EXCLAMATION =       (0b00100, 0b01110, 0b01110, 0b01110, 0b00100, nul, 0b00100, nul)
ARROW_UP =          (0b00100, 0b01110, all, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100)
ARROW_DOWN =        (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, all, 0b01110, 0b00100)

#Ambient
SUN =               (0b10101, 0b01110, all, all, 0b01110, 0b10101, nul, nul)
CLOUD =             (nul, 0b01110, 0b10001, all, nul, 0b01010, 0b00101, nul)
RAIN =              (nul, 0b01110, 0b10001, all, nul, nul, nul, nul)
SNOW =              (nul, 0b00100, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b00100)

TEMPERATURE =       (0b00100, 0b01010, 0b01111, 0b01010, 0b01010, 0b10001, 0b10001, 0b01110)
HUMIDITY =          (nul, 0b00100, 0b01110, 0b01110, 0b11101, 0b11011, 0b10111, 0b01110)
LIGHT =             (0b00100, 0b10001, 0b00100, 0b01110, 0b01110, 0b00100, 0b10001, 0b00100)

CELSIUS =           (0b11100, 0b10100, 0b11100, nul, 0b00111, 0b00100, 0b00100, 0b00111)
FAHRENHEIT =        (0b11100, 0b10100, 0b11100, nul, 0b00111, 0b00110, 0b00100, 0b00100)

#Connectivity
WIFI =              (nul, 0b01110, 0b10001, 0b00100, 0b01010, nul, 0b00100, nul)
NO_SIGNAL =         (0b01010, 0b00100, 0b01010, nul, 0b00001, 0b00001, 0b00101, 0b10101)
MQTT =              (nul, 0b00001, 0b11100, 0b00010, 0b11001, 0b00101, 0b10101, nul)

#Security
UNLOCKED =          (0b01110, 0b00001, 0b00001, all, all, 0b11011, 0b11011, all)
LOCKED =            (0b01110, 0b10001, 0b10001, all, all, 0b11011, 0b11011, all)

#Misc
ADASTRA =           (0b11011, 0b10001, 0b10110, 0b00100, 0b01100, 0b01101, 0b10001, 0b11011)

###################################
# To use with (lcd.send_bytes, RSMODE_DATA)
ARROW_RIGHT =       0b01111110
ARROW_LEFT =        0b01111111

ALPHA =             0b11100000
BETA =              0b11100010
DEGREE =            0b11011111
DIVISION =          0b11111101