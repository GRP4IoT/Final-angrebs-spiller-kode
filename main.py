import umqtt_robust2
import GPSfunk
import formel
import led_ring_funcs
import network
import ujson
from machine import Pin, reset
# ATGM336H-5N <--> ESP32
# GPS til ESP32 kredsløb
# GPS VCC --> ESP32 3v3
# GPS GND --> ESP32 GND
# GPS TX  --> ESP32 GPIO 16
import time # import sleep_ms, time.sleep, time.ticks_ms
import neopixel
from umqtt_robust2 import mqtt_sub_feedname, mqtt_sub_feedname2, c, sub_cb 
# aktuator vibrator, G-pin på GND, V-pin på 3v3, S-pin på 2
vibrator = Pin(2, Pin.OUT, value=0)

n = 12 # antallet af RGB lys på LEDringen
p = 17 # Den pin LED-ringen er tilsluttet
np = neopixel.NeoPixel(Pin(p), n) # variablen til at kontrollere LED-ringen
# LED ringens DI pin på ESP pin 17, og LED ringens V5 pin på ESP pin 5V

lib = umqtt_robust2 # variable til lettere at håndtere mqtt biblioteket
led = led_ring_funcs # variable til lettere at håndtere LED funktions biblioteket

# opret en ny feed kaldet map_gps indo på io.adafruit
mapFeed = bytes('{:s}/feeds/{:s}'.format(b'GRP4', b'mapfeed2/csv'), 'utf-8')
# opret en ny feed kaldet speed_gps indo på io.adafruit
speedFeed = bytes('{:s}/feeds/{:s}'.format(b'GRP4', b'speedfeed2/csv'), 'utf-8')
#Rssi feed
rssiFeed = bytes('{:s}/feeds/{:s}'.format(b'GRP4', b'rssi/csv'), 'utf-8')

# Variabler til at holde styr på om LED funktioner er sket
startUp = False
ledNormBack = False

# vores variabler til net ting
station = network.WLAN(network.STA_IF)
ssid = []
rssi = 0

# Vores variabel om der er offside
offside = False
forsvarAfstand = 0
offsideTest = 0

# forsøg på at implementere non-blocking delay
currentTime = 0.000 # variable til at holde styr på tid
intervalMain = 9000  # intervallet der skal ske noget
previousTimeMain = 0  # sidste gang der skete noget
# vores offside non-block delay variabler
intervalOffside = 9000
previousTimeOffside = 0
# vores netværk skanner non-block delay
intervalNet = 10000
previousTimeNet = 0

#vores reset interval
intervalReset = 12000
previousTimeReset = 0

previousTimeOpen = 0
intervalOpen = 9000

count = 0

while True:
    #gpsData = GPSfunk.main()
    currentTime = time.ticks_ms()
    GPSlist = []

    if startUp == False:
        startUp = True
        led.power_on()
        #print("POWER ON")
        time.sleep(2)

    if lib.c.is_conn_issue():
        while lib.c.is_conn_issue():
            led.trying_con() # LED ringen tændes med en bounce funktion
            # hvis der forbindes returnere is_conn_issue metoden ingen fejlmeddelse
            lib.c.reconnect()
        else:
            led.trying_con() # LED ringen tændes med en bounce funktion
            lib.c.resubscribe()
    try:
 
        if currentTime - previousTimeOpen >= intervalOpen:
            previousTimeOpen = currentTime
            #åber data_rssi.ujson filen.
            a_file = open("data_rssi.ujson", "r")
            a_json = ujson.load(a_file)
            pretty_json = ujson.dumps(a_json,)
            a_file.close()
            print(pretty_json)
            #ændre rssi filen fra et -tal til et normal tal.
            rssifloat = float(pretty_json)
            rssifloat3 = rssifloat * -1.0
            print(rssifloat3)  
        
        if currentTime - previousTimeMain >= intervalMain:
            previousTimeMain = currentTime
            led.clear()
            led.uploading()
            gpsData = GPSfunk.main()
            time.sleep(2)
            #posData = str(gpsData[0])
            #print(posData)
            lib.c.publish(topic=mapFeed, msg=gpsData[0])
            #print("efter upload" + posData)
            speed = gpsData[0]
            speed = speed[:4]
            lib.c.publish(topic=speedFeed, msg=speed)
            #print(float(gpsData[2]))
            #print(gpsData[0])
            #print(gpsData[1])
            GPSlist.append(float(gpsData[1]))
            GPSlist.append(float(gpsData[2]))
            print("egne gps coord ",GPSlist)
            count +=1

            if count >= 1:
                latA = GPSlist[0]
                lonA = GPSlist[1]
                GPScoord1 = latA, lonA
                latB = 55.70656
                lonB = 12.53932
                GPScoord2 = latB, lonB
                distance = formel.afstand(GPScoord1, GPScoord2)
                print(distance)

            #forsvarAfstand = lib.besked
            distanceforsvar = mqtt_sub_feedname
            rssi = mqtt_sub_feedname2
            
            #Printer lib.besked, som er den besked vi får fra adafruit fra GPS
            print(lib.besked)
            print('Forsvars er ',lib.besked,'m væk')
            
            #Printer lib.besked2, som er den besked vi får fra adafruit fra WifiScanner
            print(lib.besked2)
            print('forsvars er ',lib.besked2, 'dBm væk')
                        
            if lib.besked != "":
                fA = float(lib.besked)
                print(fA, type(fA))
                if fA > distance:
                    offside = True
                    print(fA, distance,'DET VIRKER!')
                else:
                    offside = False
            
#går i offside hvis rssi3 er større end rssifloat3 (laver også rssi værdien om til et normalt tal i stedet for et -tal
            if lib.besked2 != "":
                rssi = float(lib.besked2)
                rssi3 = rssi * -1
                print(rssi3, type(rssi3))
                if rssifloat3 < rssi3:
                    offside = True
                    print(rssifloat3, rssi3, 'DET VIRKER!')
            #ledNormBack = True

        if offside == True and currentTime - previousTimeOffside >= intervalOffside:
            previousTimeOffside = currentTime
            #led.offside()
            import neopixel
            n = 12
            p = 17
            np = neopixel.NeoPixel(Pin(p), n)
            for i in range(n):
                np[i] = (44, 0, 0)
                np.write()
            vibrator.value(1)
            #led.clear()
            #led.offside()
            #ledNormBack = True
            print("Potentiel offside pos")
            time.sleep(2)
            vibrator.value(0)
            #print(offsideTest)

        if ledNormBack == True:
            ledNormBack = False
            print("back to normal")
            led.power_on()
            
        #disconnecter fra wifi, og scanner efter wifi's
        if currentTime - previousTimeNet >= intervalNet:
            previousTimeNet = currentTime
            station.disconnect();
            print("hello from net")
            ssid = station.scan()
            #beder vi om RSSI værdien fra netværket LTE-1857 (RRSI er nummer 4 i rækken af værdier vi får når vi scanner)
            for i in ssid:
                if i[0] == b'LTE-1857':
                    print(i)
                    rssi = i[3]
                    print(rssi)
                    
            #Send rssi value til data_rssi.ujson filen        
            with open('data_rssi.ujson', 'w') as f:
                ujson.dump(rssi, f)
            #her resetter vi vores ESP, da den ikke kan komme på wifi igen, efter vi disconnectede den
        if currentTime - previousTimeReset >= intervalReset:
            print("resetter")
            reset()
        
    # Stopper programmet når der trykkes Ctrl + c
    except KeyboardInterrupt:
        print('Ctrl-C pressed...exiting')
        led.clear()
        #time.sleep(1)
        lib.c.disconnect()
        lib.wifi.active(False)
        lib.sys.exit()
    except OSError as e:
        print('Failed to read sensor.')
    except NameError as e:
        print('NameError', e)
    except TypeError as e:
        print('TypeError', e)

    lib.c.check_msg() # needed when publish(qos=1), ping(), subscribe()
    lib.c.send_queue()  # needed when using the caching capabilities for unsent messages

lib.c.disconnect()
