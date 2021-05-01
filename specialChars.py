all = 0b11111
nul = 0

#Communication
SMILEY_FACE =       (nul, 0b01010, 0b01010, nul, 0b10001, 0b01110, nul, nul)
SAD_FACE =          (nul, 0b01010, 0b01010, nul, 0b01110, 0b10001, nul, nul)
POKER_FACE =          (nul, 0b01010, 0b01010, nul, all, nul, nul, nul)
BIG_EXCLAMATION =   (0b00100, 0b01110, 0b01110, 0b01110, 0b00100, nul, 0b00100, nul)
ARROW_UP =          (0b00100, 0b01110, all, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100)
ARROW_DOWN =        (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, all, 0b01110, 0b00100)

#Weather
SUN =               (0b10101, 0b01110, all, all, 0b01110, 0b10101, nul, nul)
CLOUD =             (nul, 0b01110, 0b10001, all, nul, 0b01010, 0b00101, nul)
RAIN =              (nul, 0b01110, 0b10001, all, nul, nul, nul, nul)
SNOW =              (nul, 0b00100, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b00100)

#Connectivity
WIFI =              (nul, 0b01110, 0b10001, nul, 0b01110, nul, 0b00100, nul)
NO_SIGNAL =         (0b01010, 0b00100, 0b01010, nul, 0b00001, 0b00001, 0b00101, 0b10101)

#Security
UNLOCKED =          (0b01110, 0b00001, 0b00001, all, all, 0b11011, 0b11011, all)
LOCKED =            (0b01110, 0b10001, 0b10001, all, all, 0b11011, 0b11011, all)

#Misc
ADASTRA =           (0b11011, 0b10001, 0b10110, 0b00100, 0b01100, 0b01101, 0b10001, 0b11011)
