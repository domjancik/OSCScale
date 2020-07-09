from scales import Scales
from utime import sleep_ms, ticks_ms, ticks_diff
import machine
from machine import Timer
from wlan import do_connect
import json

from network import AP_IF, WLAN

from uosc.client import Client

maxValue = 50000
minValue = 0
osc = None
tim = None
scales = None
serialOut = False

lastValue = 0
lastSentMs = 0
touchedMs = 0

shouldReset = True

def map(value, srcMin, srcMax, toMin, toMax):
    return (((value - srcMin) * (toMax - toMin)) / (srcMax - srcMin)) + toMin

def updateValue(id, threshold, forceInterval):
    global minValue, maxValue, osc, scales, lastValue, lastSentMs, touchedMs, shouldReset

    val = scales.raw_value()

    maxValue = max(maxValue, val)

    rescaled = max(0, map(val, minValue, maxValue, 0, 1))
    touched = abs(rescaled - lastValue) > threshold

    if (touched or ticks_diff(ticks_ms(), lastSentMs) > forceInterval):
        lastValue = rescaled
        lastSentMs = ticks_ms()

        led.duty(int(rescaled * 1024))
        osc.send('/value/' + id, rescaled)

        if serialOut:
            print(rescaled)
    
    if touched:
        touchedMs = ticks_ms()
        shouldReset = True

    if shouldReset and ticks_diff(ticks_ms(), touchedMs) > 5000:
        # minValue = min(minValue, val)
        minValue = val
        shouldReset = False

def getConfig():
    f = open('config.json')
    config = json.load(f)
    f.close()
    return config

def blink(times):
    for i in range(times):
        led.duty(0)
        sleep_ms(60)
        led.duty(1023)
        sleep_ms(40)

if __name__ == "__main__":
    config = getConfig()
    f = open('id.txt')
    id = f.read()
    f.close()
    
    print(config)
    print('ID:' + id)

    led = machine.PWM(machine.Pin(14), freq=1000)
    blink(2)
    connected = do_connect(config['ssid'], config['password'], 20)
    if not connected:
        print('Failed to connect')
        ap = WLAN(AP_IF)
        ap.active(True)
        ap.config(essid='Tanzometr_' + id, password='tanzometR')

        while ap.active == False:
            pass

        print(ap.ifconfig())
        blink(15)
    else:
        blink(2)
        osc = Client(config['target'], config['port'])
        serialOut = config['serialOut']
        delay = config['delay']
        threshold = config['threshold']
        forceInterval = config['forceInterval']

        
        
        print("Start")    

        scales = Scales(d_out=5, pd_sck=4)
        scales.tare()
        while True:
            updateValue(id, threshold, forceInterval)
            sleep_ms(delay)

   