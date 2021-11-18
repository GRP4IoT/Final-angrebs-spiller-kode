# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
import sys
import network
sys.path.reverse()

#wifi = network.WLAN(network.STA_IF)
#wifi.active(True)
#wifi.connect("LTE-1857", "12345678")
