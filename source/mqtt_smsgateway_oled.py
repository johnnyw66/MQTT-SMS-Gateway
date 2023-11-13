# Import libraries - config.py sets up wifi and mqtt
 
import time
import json

from mqtt_as import MQTTClient, config
from config import wifi_led, blue_led  # Local definitions
import uasyncio as asyncio
import machine
from machine import Pin, PWM, I2C

from time import sleep

from machine import UART
from queue import Queue

from ssd1306 import SSD1306_I2C
import framebuf
import machine
import random
import pickle


DONGLEID = 'donglePICO_CMD'
SMSOUT_TOPIC = 'smsoutnew'
HEARTBEAT_TOPIC = 'smsgwheartbeat'
SYSTEM_CMD_TOPIC = 'cmd'




indicator_delay = 3000
sms_message = None

# OLED Stuff

WIDTH  = 128                                            # oled display width
HEIGHT = 32                                            # oled display height
sda =Pin(14)
scl =Pin(15)
rst = Pin(26, mode=Pin.OUT, value=1)                   # GSM 800L RESET PIN - Pull low to Reset
FB_WIDTH = 32
FB_HEIGHT = 32


message = None
message_count = 0
time_between_messages = 0

async def update_message_timer():
    global time_between_messages
    while True:
        await asyncio.sleep(1)
        time_between_messages  = time_between_messages + 1

async def reset_message_timer():
    global time_between_messages
    time_between_messages = 0
    
async def reset_sim800():
    print("reset_sim800()")
    rst.value(0)
    await asyncio.sleep_ms(5)
    rst.value(1)

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


def add_message(in_message):
    global message, message_count
    message_count = message_count + 1
    message = in_message
    
    
def font_width(message):
    return len(message) * 8

def font_height():
    return 8

async def oled_message_loop():
    global message, message_count
    oled = None
    while not oled:
        oled =  await get_oled(sda, scl, 400000)
        await asyncio.sleep_ms(2000)
        
    print(oled, message)
    #buffer = bytearray([0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x7c,0x00,0x00,0x00,0x82,0x00,0x00,0x00,0x82,0x00,0x00,0x00,0x82,0x00,0x00,0x00,0xfe,0x00,0x00,0x00,0x82,0x00,0x00,0x00,0x82,0x10,0x00,0x00,0x82,0x10,0x00,0x00,0x82,0x38,0xc1,0xfc,0x00,0x11,0x20,0x04,0x00,0x11,0x20,0x08,0x00,0x0c,0xc0,0x10,0x00,0x00,0x00,0x20,0x00,0x00,0x00,0x40,0x00,0x00,0x00,0x80,0x00,0x00,0x01,0x00,0x00,0x00,0x01,0xfc,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x7c,0x7c,0xfe,0x00,0x82,0x82,0x10,0x00,0x82,0x82,0x10,0x00,0x82,0x82,0x10,0x00,0xfc,0x82,0x10,0x00,0x82,0x82,0x10,0x00,0x82,0x82,0x10,0x00,0x82,0x82,0x10,0x00,0x7c,0x7c,0x10,0x00])
    
    buffer=bytearray([0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x7c,0x30,0xc3,0xe0,0x82,0x49,0x24,0x10,0x80,0x46,0x24,0x00,0x80,0x40,0x24,0x00,0x7c,0x40,0x23,0xe0,0x02,0x40,0x20,0x10,0x02,0x40,0x20,0x10,0x82,0x40,0x24,0x10,0x7c,0x40,0x23,0xe0,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x1c,0x39,0xf3,0x80,0x20,0x44,0x44,0x00,0x20,0x44,0x44,0x1e,0x27,0x7c,0x47,0x80,0x22,0x44,0x44,0x00,0x1c,0x44,0x43,0x80,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x20,0x9c,0x88,0x00,0x20,0xa2,0x50,0x00,0x20,0xa2,0x20,0x00,0x24,0xbe,0x20,0x00,0x15,0x22,0x23,0x00,0x0a,0x22,0x23,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])


    logo_fb = framebuf.FrameBuffer(buffer, FB_WIDTH, FB_HEIGHT, framebuf.MONO_HLSB)
    
    xoffset = 0
    while True:
        xoffset = xoffset + 1
        x = xoffset % (1 if not message else font_width(message)  - (WIDTH*0//1))
        try:
            if (oled):
                oled.fill(0)
                oled.blit(logo_fb, WIDTH - FB_WIDTH, 0)
                oled.text( message or "" , -x, FB_HEIGHT//2)
                oled.text( f"{str(message_count)}" , 8, 8)
                oled.text( f"{str(time_between_messages)}" , 8, HEIGHT - font_height())
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


# End of OLED Stuff

class NetworkException(Exception):
    def __init__(self, msg):
         self.message = msg
    def __str__(self):
        return f"NetworkException: {self.message}"
    
class SMSMessage:
    def __init__(self, headers, message=''):
        self.headers = headers
        self.message = message
    
    def append(self, str):
        self.message += str

    def __str__(self):
        return f"SMSMessage: headers: {self.headers} msg: <{self.message}>"



# MQTT Message Subscription and Display
def sub_cb_factory(gsm_cmd_queue):

    async def add_gsm_command(command):
        await gsm_cmd_queue.put(command)

    def clean_phone_number(phone_str):
        return phone_str if phone_str[0]=='+' else '+'+phone_str
        #return phone_str
    
    
    def sub_cb(topic, msg, retained):
        
         dtopic = topic.decode()
         dmsg = msg.decode()
         
         print(f'Topic {dtopic} Message: "{dmsg}"  Retained: {retained}')
         if (SMSOUT_TOPIC in dtopic):

             # This is a fudge - there is no AST in Micropython to simply
             # parse our javascript JSON string - so allow for simple
             # text strings only. The following will fail if there are single quotes
             # in our value fields - (i.e the sms text field)
             
             cleaned_dmsg = dmsg.replace("'", "\"")
             sms = json.loads(cleaned_dmsg)

             msgtext=sms['text']
             destphone = clean_phone_number(sms['to'])
             print(f"SMSOUT to:'{destphone}' text:'{msgtext}'")
             asyncio.create_task(add_gsm_command(f'AT+CMGS="{destphone}"\n{msgtext}\x1A\r\n'))
         
         elif (SYSTEM_CMD_TOPIC in dtopic):

             print(f"COMMAND {dmsg}")
         
         else:
             print(f"Unrecognised topic {dtopic}")
             pass
        

            
    return sub_cb

async def mqtt_heartbeat_loop(client, delay_in_secs = 60):
    global message_count, time_between_messages
    while True:
        print(f"mqtt_hearbeat_loop")
        payload = str({ 'id' : f'{DONGLEID}', 'sms_in':message_count, 'last_sms':time_between_messages})
        await client.publish(f"{HEARTBEAT_TOPIC}/{DONGLEID}", payload, False, 1)
        await asyncio.sleep(delay_in_secs)  


async def gsm_networkconnection_loop(gsm_cmd_queue, delay_in_secs = 45):
    while True:
        print(f"GSM Network Connection Test")
        await gsm_cmd_queue.put('AT+COPS?\r\n')
        await asyncio.sleep(delay_in_secs)  

async def message_complete(message):
    print(f"{message}")
    
async def parse_responses(response, gsm_cmd_queue, sms_queue):
    global sms_message, indicator_delay
    
    params=response.split(',')
    #print(f"parse_responses: {params}")
    if (sms_message is not None):
        # Building a text message after receiving an AT '+CMGR' response
        sms_message.append(response)
        if '\r\n' in response:
            await message_complete(sms_message)
            await sms_queue.put(SMSMessage(sms_message.headers, sms_message.message))
            await reset_message_timer()
            sms_message = None
    elif params[0] == "RING\r\n":
        print("RING")
    elif params[0][0:5] == "+CLIP":
        incoming_call_from = params[0][6:].strip()[1:-1]
        print("CLIP---->", incoming_call_from)
    elif params[0][0:5] == "+CMTI":
        msgid = int(params[1])
        await gsm_cmd_queue.put(f'AT+CMGR={msgid}\n')
        await gsm_cmd_queue.put(f'AT+CMGD={msgid}\n')
    elif params[0][0:5] == "+CMGR":
        #print(f"READING A TEXT MESSAGE ")
        sms_message = SMSMessage(params[1:]) # Start to build the sms text message
    elif params[0][0:5] == "+COPS":
        print("COPS CHECK", len(params), params)
        if (len(params) != 3):
            #raise NetworkException("Network Not Connected.")
            indicator_delay = 3000
        else:
            indicator_delay = 500
            
        #return len(params) == 3
async def uart_read_loop(uart, response_queue):
    print(f"uart_read_loop queue = {response_queue}")
    while True:
        if uart.any():
            data = uart.readline()
            response = data.decode('utf-8')
            await response_queue.put(response)
            #print(f"uart_read_loop: response = {response} added to response queue - size = {response_queue.qsize()}")
            
        await asyncio.sleep_ms(1)  # Wait for 1 mseconds between messages

    
async def uart_write_loop(uart, message_queue):
    print("uart_write_loop")
    while True:
        message = await message_queue.get()  # Wait for a message from the queue
        #print(f"WRITE {message}")
        uart.write(message.encode('utf-8'))  # Write message to UART
        await asyncio.sleep_ms(2000)  # Wait for 2 seconds between messages

async def response_handler(response_queue, message_queue, sms_queue):
    print(f"response_handler queue = {response_queue}")
    while True:
        response = await response_queue.get()
        await parse_responses(response, message_queue, sms_queue)
        await asyncio.sleep_ms(1000)  # Wait for 1 seconds between messages
       
    
# Demonstrate scheduler is operational.
async def heartbeat():
    global indicator_delay
    
    s = True
    while True:
        await asyncio.sleep_ms(indicator_delay)
        blue_led(s)
        s = not s

async def wifi_han(state):
    wifi_led(not state)
    print('Wifi is ', 'up' if state else 'down')
   # sweep()
    await asyncio.sleep(1)

async def publish_incoming_sms_loop(client,sms_queue):
    global message
    
    while True:
        if not sms_queue.empty():
            sms = await sms_queue.get()
            to = f"{DONGLEID}"
            mo = sms.headers[0][1:-1]
            dt = sms.headers[2][1:]
            tm = sms.headers[3][:-3]
            payload = str({ 'msisdn' : mo, 'to' : to, 'text' : sms.message, 'date' : dt, 'time' : tm})

            add_message(sms.message.replace('\r','').replace('\n',' '))	# Display SMS updates on OLED if one is on our bus.
            
            await client.publish(f"mqttsmsgw/{to}", payload, False, 1)

        await asyncio.sleep_ms(500)
    
# If you connect with clean_session True, must re-subscribe (MQTT spec 3.1.2.4)
async def conn_han(client):
    
    # MQTT Subscirbe Topic listen for instructions to send SMS or System Commands

    await client.subscribe(f'{SMSOUT_TOPIC}/{DONGLEID}', 1)
    await client.subscribe(f'{SYSTEM_CMD_TOPIC}/{DONGLEID}', 1)

async def main(client, gsm_command_queue):
    start_up_commands = [
        "AT\r\n",
        "AT+CMGF=1\r\n",
        "AT+CMGD=1,4\r\n"
        #"AT+COPS?\r\n",
        #f'AT+CMGS="{destphone}"\n{msgtext}\x1A\r\n',
    ]


    try:
        for command in start_up_commands:
            #print(f"put {command} in queue")
            await gsm_command_queue.put(command)
        await client.connect()

    except OSError:
        print('Connection failed.')
        machine.reset()
        return
    # Allow us to change link and force setup mode 
    option = Pin(10, mode=Pin.IN, pull=Pin.PULL_UP)
    while True:
        await asyncio.sleep(5)
        if (option.value() == 0):
            machine.reset()   


indicator_delay = 3000

# Define configuration
gsm_command_queue = Queue()
gsm_response_queue = Queue()
sms_queue = Queue()

# Look at last Saved Config Pickle File 
with open('saved_dictionary.pkl', 'rb') as f:
    params = pickle.load(f)

config['server'] = params['mqhost'] #'213-219-39-111.ip.linodeusercontent.com'
config ['port'] = int(params['mqprt']) #1883
config['user'] = params['mquser'] #'sms2'
config ['password'] = params['mqsec'] #'johnny66' 

config['ssid'] = params['apn']
config['wifi_pw'] = params['appwd']

# DongleID
DONGLEID = f"dongle{params['dongid']}"


config['subs_cb'] = sub_cb_factory(gsm_command_queue)
config['wifi_coro'] = wifi_han
config['connect_coro'] = conn_han
config['clean'] = True

print(DONGLEID)
print(config)


time.sleep(10)

# Set up client
MQTTClient.DEBUG = True  # Optional
client = MQTTClient(config)

uart = UART(0, baudrate=19200, tx=Pin(16), rx=Pin(17), timeout=500)

#asyncio.create_task(reset_sim800())

asyncio.create_task(oled_message_heartbeat())
asyncio.create_task(oled_message_loop())

asyncio.create_task(update_message_timer())
asyncio.create_task(heartbeat())
asyncio.create_task(uart_read_loop(uart, gsm_response_queue))
asyncio.create_task(uart_write_loop(uart, gsm_command_queue))
asyncio.create_task(response_handler(gsm_response_queue, gsm_command_queue, sms_queue))
asyncio.create_task(publish_incoming_sms_loop(client, sms_queue))
asyncio.create_task(gsm_networkconnection_loop(gsm_command_queue))
asyncio.create_task(mqtt_heartbeat_loop(client))


try:
    asyncio.run(main(client, gsm_command_queue))
    

finally:
    client.close()  # Prevent LmacRxBlk:1 errors
    asyncio.new_event_loop()




