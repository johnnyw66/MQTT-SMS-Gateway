from machine import Pin, I2C

from time import sleep
import uasyncio as asyncio
import network
import time
#import socket
import usocket as socket
import re
from ssd1306 import SSD1306_I2C
import framebuf
import machine
import pickle
import dns

WIDTH  = 128                                            # oled display width
HEIGHT = 32
FB_WIDTH = 32
FB_HEIGHT = 32
sda =Pin(14)
scl =Pin(15)
AP_NAME = "mqttsmsgw"
AP_PASSWORD="smsgateway"


def generate_form(params):
    print("Generate Form")

    apname = params['apn'] if 'apn' in params else ''
    appass = params['appwd'] if 'appwd' in params else ''
    mqtthost = params['mqhost'] if 'mqhost' in params else '127.0.0.1'
    mqttport = params['mqprt'] if 'mqprt' in params else '1883'
    mqttuser = params['mquser'] if 'mquser' in params else ''
    mqttsecret = params['mqsec'] if 'mqsec' in params else ''
    donglename = params['dongid'] if 'dongid' in params else 'PICO'

    
    return f"""
        <form action='/save'>
        <label for='apname'>AP Name</label>
        <input type='text' name='apn' id='apn' value='{apname}'>

        <label for='appasswd'>AP Password</label>
        <input type='password' name='appwd' id='appwd' value='{appass}'><br>

        <label for='mqtthost'>MQTT Host</label>
        <input type='text' name='mqhost' id='mqhost' value='{mqtthost}'>

        <label for='mqttport'>MQTT Port</label>
        <input type='text' name='mqprt' id='mqprt' value='{mqttport}'>

        <label for='mqttuser'>MQTT User</label>
        <input type='text' name='mquser' id='mquser' value='{mqttuser}'>

        <label for='mqttsecret'>MQTT Secret</label>
        <input type='password' name='mqsec' id='mqsec' value='{mqttsecret}'><br>

        <label for='donglename'>Dongle ID</label>
        <input type='text' name='dongid' id='dongid' value='{donglename}'><br>
  
        <input type="submit" value="Submit">

        </form>
"""

def web_page(request_url, par, params):
    if ('favicon' in request_url):
        print("*****FAVICON*****")
        return "OK"
    if ('save' in request_url):
        with open('saved_dictionary.pkl', 'wb') as f:
            pickle.dump(params, f)
    else:
        with open('saved_dictionary.pkl', 'rb') as f:
            params = pickle.load(f)
            print(params)
    
    html = f"""<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
            <body>
                <h1>MQTT SMS GATEWAY SETUP.</h1><p>{request_url}</p><p>{par}</p><p>params={params}</p>
                {generate_form(params)}
            </body></html>
         """
  
    return html

def build_params(params_str):
    return {_[0]:_[1].strip() for _ in [ _.split('=') for _ in params_str[1:].split("&")]}  if params_str.startswith('?') else {}

    
def page_helper(request):
    print(f"page_helper:{request}")
    pattern = r"GET (/\w*)(.*)HTTP/1.1"
    match = re.search(pattern, request)
    if (match):
        print("GROUP 2",match.group(2))
        matched_substring = match.group(0) 
        captured_group = match.group(1)
        params = build_params(match.group(2))

        print("Matched substring:", matched_substring)
        print("Captured groups:", captured_group, params)
        response=web_page(request,captured_group, params)
    else:
        response = "HTTP/1.0 405 Method Not Allowed\r\n\r\nMethod not allowed\r\n"
    return response


def client_factory(page_helper):

    print("client factory", page_helper)
    
    async def handle_httpclient(reader, writer):
        print("Handle Client",page_helper)
        request_line = await reader.readline()
        print(">>>>>Request:", request_line)
        # We are not interested in HTTP request headers, skip them
        while await reader.readline() != b"\r\n":
            pass


        print("Handle Client",reader,writer)
        request = request_line.decode('utf-8')
        print(">>>>>>Request", request)
        response = page_helper(request)
        
        writer.write(response.encode('utf-8'))
        await writer.drain()
        await writer.wait_closed()

    return handle_httpclient


async def ap_mode(ssid, password):
    global message

    print("AP MODE SET UP")
    
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ssid, password=password)
    ap.active(True)
    
    while ap.active() == False:
        pass
    print('AP Mode Is Active, You can Now Connect')
    message  = f'{AP_NAME}:{AP_PASSWORD} {ap.ifconfig()[0]} ' * 2
    return ap.ifconfig()[0]



def font_width(message):
    return len(message) * 8

async def get_oled(sda, scl, freq):

    try:
        i2c=I2C(1, sda=sda, scl=scl, freq=freq)
        print("I2C Address      : "+hex(i2c.scan()[0]).upper()) # Display device address
        print("I2C Configuration: "+str(i2c))                   # Display I2C config
        return SSD1306_I2C(WIDTH, HEIGHT, i2c)
    except IndexError as ie:
        print("I2C device not plugged in")
        return None
    except OSError as oe:
        print("Device Error")
        return None

async def oled_message_loop():
    global message
    oled = None
    while not oled:
        oled =  await get_oled(sda, scl, 400000)
        await asyncio.sleep_ms(2000)
        
    print(oled, message)
    buffer = bytearray([0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x7c,0x00,0x00,0x00,0x82,0x00,0x00,0x00,0x82,0x00,0x00,0x00,0x82,0x00,0x00,0x00,0xfe,0x00,0x00,0x00,0x82,0x00,0x00,0x00,0x82,0x10,0x00,0x00,0x82,0x10,0x00,0x00,0x82,0x38,0xc1,0xfc,0x00,0x11,0x20,0x04,0x00,0x11,0x20,0x08,0x00,0x0c,0xc0,0x10,0x00,0x00,0x00,0x20,0x00,0x00,0x00,0x40,0x00,0x00,0x00,0x80,0x00,0x00,0x01,0x00,0x00,0x00,0x01,0xfc,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x7c,0x7c,0xfe,0x00,0x82,0x82,0x10,0x00,0x82,0x82,0x10,0x00,0x82,0x82,0x10,0x00,0xfc,0x82,0x10,0x00,0x82,0x82,0x10,0x00,0x82,0x82,0x10,0x00,0x82,0x82,0x10,0x00,0x7c,0x7c,0x10,0x00])
    logo_fb = framebuf.FrameBuffer(buffer, FB_WIDTH, FB_HEIGHT, framebuf.MONO_HLSB)
    
    xoffset = 0
    while True:
        xoffset = xoffset + 1
        x = xoffset % (1 if not message else font_width(message)  - (WIDTH*0//1))
        try:
            if (oled):
                oled.fill(0)
                #oled.blit(logo_fb, WIDTH - FB_WIDTH, 0)
                oled.text( message or "" , -x, FB_HEIGHT//2)
                oled.show()
        except OSError as oe:
            print(f"OSError {oe}")
        await asyncio.sleep_ms(25)


async def oled_message_heartbeat():
    
    s = True
    while True:
        await asyncio.sleep_ms(2000)
        print(f"oled_message_heartbeat {s}")
        s = not s

async def main():
    print("Main")
    option = Pin(10, mode=Pin.IN, pull=Pin.PULL_UP)

#    with open('saved_dictionary.pkl', 'wb') as f:
#        pickle.dump({}, f)
    
    ip = await ap_mode(AP_NAME, AP_PASSWORD)
    #dns.run_catchall(ip)

    while True:
#
        print("check option link.")
        await asyncio.sleep(5)
        if (option.value() == 1):
            print("RESETTING")
            await asyncio.sleep(5)
            machine.reset()

message=""

asyncio.create_task(oled_message_heartbeat())
asyncio.create_task(oled_message_loop())
asyncio.create_task(asyncio.start_server(client_factory(page_helper), '0.0.0.0', 80))

try:
    asyncio.run(main())
    
finally:
    asyncio.new_event_loop()
