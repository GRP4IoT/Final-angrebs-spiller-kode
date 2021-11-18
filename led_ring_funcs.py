from time import sleep, sleep_ms, ticks_ms
from machine import Pin
import neopixel

n = 12 # antallet af RGB lys på LEDringen
p = 17 # Den pin LED-ringen er tilsluttet

np = neopixel.NeoPixel(Pin(p), n)

# LED ringen bliver slukket
def clear():
    for i in range(n):
        np[i] = (0, 0, 0)
        np.write()
    print("LED OFF")

# LED-ringen er bare fuldt tændt grøn
def power_on():
    for i in range(n):
        np[i] = (25, 25, 0)
        np.write()
    print("POWER ON")
    
def uploading():
    for i in range(n):
        np[i] = (6, 6, 29)
        np.write()
    print("Uploading")
    
def offside():
    for i in range(n):
        np[i] = (29, 20, 0)
        np.write()
    print("Offside")

# cyclus af lys (cirkel løb)
def low_power():
    print("LOW POWER")
    for i in range(16 * n):
        for j in range(n):
            np[j] = (0, 0, 0)
        if (i // n) % 2 == 0:
            np[i % n] = (29, 0, 0)
        sleep_ms(50)
        np.write()

# LED ringen bouncer frem og tilbage
def trying_con():
    for i in range(16 * n):
        for j in range(n):
            np[j] = (29, 23, 0)
        if (i // n) % 2 == 0:
            np[i % n] = (0, 0, 0)
        else:
            np[n - 1 - (i % n)] = (0, 0, 0)
        sleep_ms(50)
        np.write()
