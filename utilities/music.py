
#Controllare SEMPRE che le virgole qui siano a posto

notes = {
    "C" : 261.63,
        
    "C#" : 277.18,
    "Db" : 277.18,
        
    "D" : 293.66,
        
    "D#" : 311.13,
    "Eb" : 311.13,
        
    "E" : 329.63,
    "F" : 349.23,
        
    "F#" : 369.99,
    "Gb" : 369.99,
        
    "G" : 392,
        
    "G#" : 415.30,
    "Ab" : 415.30,
        
    "A" : 440,
    
    "A#" : 466.16,
    "Bb" : 466.16,
        
    "B" : 493.88
}

#Anche e soprattutto qui

sequenceStartTone = [
        ("B", 0, 1/16), ("P", 1/16), 
        ("F#", -1, 1/32), ("P", 3/32), 
        ("F#", 1, 1/16), ("P", 1/16),
        ("D#", 1, 1/16),
        ("F#", 1, 1/32),
        ("A#", 1, 1/32),
        ("B", 1, 1/6)
    ]

welcomeTone = [
        ("F#", 0, 1/24), ("P", 3/24), 
        ("F#", 0, 1/24), ("P", 1/24), 
        ("C#", 1, 1/24), ("P", 1/24),
        ("A#", 0, 1/24), ("P", 1/24), 
        ("C#", 1, 1/24), ("P", 1/24), 
        ("F#", 1, 1/24), ("P", 1/24), 
    ]

waitTone = [
        ("G#", 0, 1/16), ("P", 1/16), 
        ("G#", -1, 1/16),
    ]

successTone = [
        ("G", 0, 1/32), ("P", 1/32), 
        ("D", 1, 1/32), ("P", 1/32), 
        ("B", 1, 1/32), ("P", 3/32),
        ("D", 1, 1/32), ("P", 3/32),
        ("G", 1, 1/16) 
    ]