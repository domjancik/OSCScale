from network import WLAN, STA_IF

def do_connect(ssid, password, tries=10):
    from time import sleep
    sta_if = WLAN(STA_IF)

    if not sta_if.isconnected():
        sta_if.active(True)
        sta_if.connect(ssid, password)

        for i in range(tries):
            print('Connecting to network (try {})...'.format(i+1))
            if sta_if.isconnected():
                print('network config:', sta_if.ifconfig())
                break

            sleep(1)
        else:
            print("Failed to connect in {} seconds.".format(tries))
            sta_if.active(False)
            return False
    else:
        print('network config:', sta_if.ifconfig())
    
    return True

def is_connected():
    sta_if = WLAN(STA_IF)
    return sta_if.isconnected()