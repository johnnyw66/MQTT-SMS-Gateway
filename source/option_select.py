from machine import Pin
# Option select on Pin GP21
option = Pin(21, mode=Pin.IN, pull=Pin.PULL_UP)
if (option.value() == 1):
    print("PULL UP")
    import mqtt_smsgateway_oled
else:
    print("PULL DOWN")
    import config_server_ap


    






