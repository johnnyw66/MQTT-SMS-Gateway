# MQTT-SMS-Gateway

Included here is a hardware and software description of a SMS MQTT Gateway, useful for automating one time password (OTP) authentication.
Although this text comments on the webscraping process - the main purpose of this writeup is to explain and show how to build a IoT device to handle incoming SMS.

A working webscraping example - will be given in another git respository.

(WATCH THIS SPACE FOR A LINK)

https://github.com/johnnyw66/cookie_session

## Webscraping

Writing a web scraper that relies on SMS for One Time Passwords (OTP) as part of its authentication stage can be a bit challenging due to the dynamic and secure nature of OTPs. Here's a high-level overview of how you might approach building such a scraper:

Firstly, You need to automate the authentication process, which typically involves:

* Navigating to the login page.
* Providing credentials (username and password).
* Triggering the OTP request.
* Receiving and inputting the OTP. (Usually on your Mobile Device)
* Submitting the verification code on a form.

![Typical OTP Authentication Flow](/images/typical-auth-flow.png)


## Use a Real Mobile Number and Receive OTPs:
***

To receive OTPs, you'll need access to a mobile number. You might use your own phone or a virtual mobile number service that provides APIs to receive SMS. Some main Virtual number providers are Vonage, Twilio and MessageBird.

Most of these virtual services will allow the user to specify a HTTP endpoint which will be triggered in the event of an incoming SMS.

However, it is my experience that these service providers do not like you to use their services for authentication.
This means that they will not forward traffic with pharses with words containing **'verification code'**. Anyhow, even if you found an agreeable API provider - you would have to pay a price for renting a virtual number, plus ongoing costs for each SMS message forwarded to your own web hook. This could be costly!


Receive and Extract OTPs on your own GSM Hardware:

The project in this repository, explains the hardware and software of a solution for OTP handling, using a messaging protocol known as MQTT. Incoming messages are received by microprocessed controlled GSM hardware and broadcasted to those beneficiary applications as a simple JSON object wrapped up as an MQTT message. 
```
{
"from": "Amazon",
 "msdn":"+447001234",
"text":"Your verification code is 791985 - please use this to ..."
}
```

![Authentication Using MQTT](/images/mqtt-auth-flow.png)


In MQTT SMS Gateway, I've added the capability to send text messages - so you can use it for sending small information to your mobile phone. For example, you could use it to send a text message in the event of some alarm being triggered in your own home. The gateway becomes even more powerful when paired up with **NodeRed**, a GUI server application which can handle MQTT messages which can trigger Node-js applicatons. There's a plethora of add-ons for **NodeRed** which offer support for processing input data and sending that processed data onto external servers or other applications.

![Example NodeRed Flow - Generate Echo Dot annoucements if webscraping sucessfully completed its required task](/images/nodered.png)


## What is MQTT?

Message Queuing Telemetry Transport (MQTT), is a lightweight and efficient messaging protocol designed for low-bandwidth, high-latency, or unreliable networks. An MQTT broker is a central component of the MQTT messaging system that plays a crucial role in facilitating communication between clients. Here's what an MQTT broker does:

1.	Message Routing: The MQTT broker is responsible for receiving messages from MQTT clients and routing them to the appropriate destinations. Clients can subscribe to specific "topics" of interest, and the broker ensures that messages sent to those topics are delivered to the subscribed clients.

2.	Publish-Subscribe Model: MQTT operates on a publish-subscribe model. Clients can publish messages to specific topics, and other clients can subscribe to those topics to receive messages. The broker manages the distribution of messages to the subscribers, allowing for one-to-many communication.

3.	Quality of Service (QoS): The MQTT protocol provides different levels of message delivery assurance, known as Quality of Service (QoS). The broker is responsible for ensuring that messages are delivered according to the specified QoS level, which can range from at most once (fire and forget) to at least once (guaranteed delivery) to exactly once (guaranteed delivery with no duplicates).

4.	Client Authentication and Authorization: MQTT brokers typically support authentication mechanisms to verify the identity of clients. They can also implement authorization rules to control which clients are allowed to publish or subscribe to specific topics.

5.	Retained Messages: MQTT brokers can store retained messages on specific topics. These messages are sent to new subscribers when they first subscribe to a topic, ensuring that clients receive the latest information even if they join a topic late.


Overall, an MQTT broker is the core component of the MQTT ecosystem, responsible for managing the routing, delivery, and reliability of messages between MQTT clients in various applications, including IoT, telemetry, and messaging systems.

## What are the Advantages of Decoupling OTP from the actual Webscraping?

Decoupling OTP authentication can make it easier to replace or upgrade certain components or technologies without affecting the rest of the system. This is crucial for adapting to changing requirements or taking advantage of new hardware and software technologies.

Who knows, perhaps one day we can find a virtual service that does not filter/block SMS traffic.

One additional benefit is that webscraping system will be more resilant against failures - since we can run multiple scrapers on different servers and at different locations.


## Why do 'Pure' Python Webscrapers behave differently to Desktop Web browsers?

Python webscrapers complete their tasks, usually by completing web forms for authentication and using a server's restFul API to filter out data.
They behave as if they were client web browsers running without Javascript - and so not all Cookies are generated in the autentication process.

Simple Python webscrapers can only receive those cookies from HTTP response headers ('Set-Cookie').

Without these Javascript-set cookies you often find an inherent behaviour that is different from interacting with Desktop web broswer.
A good example would be that the Python webscraper would only have a very limited time scrapping data from a site before having to go through full reauthentication.
On Amazon's AtoZ website - the time limit is 900 seconds.

If you want to simulate this difference using a Chrome web browser- try disabling javascript in the browser's settings.

## How can I circumvent the lack of a full cookie set?

You could try and write a Python webscraper using **Selenuim**.

**OR**

Write a Cookie extractor on your Desktop/Laptop that you use to view your data provider's (like AtoZ) website using a normal browser and use this
to populate cookies for your Python webscraper. Often, you can use a 'Trusted Device' option set within the authentication system, avoiding the OTP process for 30 days.

## I like the idea of extracting cookies - Can I use this with a Python webscraper?

You bet! You can 'publish' a serialised JSON 'topic' of the neccessary cookies (an HTTP session) using MQTT.

A Webscraper can 'subscribe' to this - picking up any new sessions. Take a look at the Python libraries *json* and *jsonpickle*

On AtoZ - You'll have to run this 'refresh' session process every 30 days.

## You haven't said much about 'Selenium' - What is that?


In short, Python Selenium is a popular library for automating web browsers, and needs to be used with a 'WebDriver' for a particular browser, (Chrome, Firefox, Edge)


Here's a breakdown of what Python Selenium and the most popular (Chrome) WebDriver can do:

Python Selenium:

Selenium is an open-source framework for automating web browsers. It provides a programming interface to control the behavior of web browsers and perform various tasks programmatically, such as navigating to websites, filling out forms, clicking buttons, and scraping data from web pages.
It supports various web browsers, including Chrome, Firefox, Edge, and others, allowing you to choose the browser that best suits your needs.
Selenium can be used for various purposes, such as web testing, web scraping, and automating repetitive tasks that involve interacting with web applications.

Chrome WebDriver:

The Chrome WebDriver is a part of Selenium that enables interaction with the Google Chrome browser. Each major web browser, including Chrome, Firefox, and Edge, has its own WebDriver component.
The WebDriver acts as a bridge between your Python code and the web browser. It allows you to send commands to the browser to simulate user interactions.
You can use the Chrome WebDriver to open Chrome, navigate to websites, interact with web elements (like clicking buttons, entering text, and selecting items from dropdowns), and extract data from web pages.
The Chrome WebDriver supports various programming languages, including Python, Java, C#, and more. In the context of Python, you can use the Selenium library along with the Chrome WebDriver to automate tasks in Google Chrome. There are additional flags when running the WebDriver - such as running browser interaction without a GUI display.

As an example, check the following Python snippet below - which logs into a Web service, filling in the user and password fields.

```
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")

s = Service('/Users/johnny/sessionbot/chromedriver' if platform.system() == 'Darwin' else '/usr/bin/chromedriver')
driver = webdriver.Chrome(service=s, options=chrome_options)  

wait = WebDriverWait(driver, 10)

driver.get('https://atoz.amazon.work/login');

buttonLogin = wait.until(EC.presence_of_element_located((By.ID, "buttonLogin")))
name = driver.find_element(By.ID,'login')
password = driver.find_element(By.ID,'password')

name.send_keys(configure.ATOZ_USERNAME)
password.send_keys(configure.ATOZ_PASSWORD)
buttonLogin.submit()
logging.info("Submitting AtoZ credentials.")

```
At some point in the process of logging into a web service we may need to go through the OTP process.

```
# Wait for OTP over MQTT
verification_timeout = config.OTP_TIMEOUT
verification_start = time.time()

while verification_code is None:
    client.loop(timeout=1.0) # Allow MQTT to run - in order to receive the verification code
    time_passed = int(time.time() - verification_start)
    if ( time_passed > verification_timeout):
        logging.info("Timed out - Raising VerificationException")
        raise VerificationException("Missing Verification - Just Leave")

logging.info(f"VERIFICATION CODE IS {verification_code}")

button_verify_identity = wait.until(EC.presence_of_element_located((By.ID, "buttonVerifyIdentity")))
otp_code = driver.find_element(By.ID,'code')
trusted_device_checkbox = driver.find_element(By.ID, 'trustedDevice')

otp_code.send_keys(verification_code)
trusted_device_checkbox.click()
button_verify_identity.submit()

```

The various Selenuim Python libraries support waiting for page loading - making sure you don't miss out on important data - due to the asynchronous nature of web browsing.
If you are familiar with DOM handling in javascript - you will probably be comfortable with writing code to search for HTML elements. Selenium 'bot' coding uses a lot of searching for elements, generating input actions such as clicking buttons or submitting forms. The code above is tightly coupled to the names of elements in a web servers web pages, meaning it will fail if the any of the element identities are changed.



## Selenium sounds great - Why don't you use that?

I have done - and it works fairly well - up to the point where a website host changes its pages. My ambition is to make a webscraper that can run on a £5.00 IoT micropython processor.
Pure Python Restful API webscrapers will miss out on data which is dynamically generated through Javascript but its main advantage is speed!
Normally, websites only use Javascript to build a VIEW of the data that has already been downloaded to the browser. (Though it appears that AtoZ actually generates some cookies using Javascript)

Selenium has the disadvantage that you need to have matching pairs of a GUI Web Browser and Driver installed - meaning that this is only possible to run on Desktop OS such as Linux/MacOS or Windows OS.

## Do I need the MQTT SMS Gateway for web scraping operations?

No you don't. You could in theory start logging in on your Web Service (eg. AtoZ) and go through OTP on your mobile. Once you've gone through authentication, you can run some Python code to view and replicate the browsers cookies for the domain(s) of the webservice to start a Python session using the popular HTTP **requests** library. This could mean being able to run a Web Scraper for days or weeks without going through OTP.
There are a few software hurdles you have to get over in order to copy browser cookies. The popular browsers save cookies in a database (usually **Sqlite3**) - encrypting the cookie value field. 

```
        # Snippet of Python code which extracts cookies from the Chrome database file
 
        copy(self.cookies_db_path, "cookies.db")
        conn = sqlite3.connect("cookies.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT name, encrypted_value, host_key, path, expires_utc FROM cookies WHERE host_key LIKE '%{host}'")

        data = {'data': []}
        for result in cursor.fetchall():
            name, encrypted_value, host_key, path, expires_utc = result 

            value = self.chrome_os.decrypt_func(encrypted_value)

            _data = {}
            _data['name'] = name
            _data['value'] = value
            _data['domain'] = host_key
            _data['path'] = path
            _data['expires'] = expires_utc

            data['data'].append(_data)
        conn.close()
        unlink("cookies.db")
```
You can see from the code above that the actual stored values of a cookie need to go through a **decryption function** - (in the 90s cookies where stored in plain unencrypted text files) - so there is some work needed to decrypt the actual value. Unfortunately, the decryption algorithm for this changes with the browser and operating system.


All is not lost, mind. Most browsers have been developed under the 'Open Source' umbrella, meaning that if you are confident with programming in diffent languages - you can find those bits relevant to the encryption and decryption of cookies and port code to Python.



### Building your MQTT SMS Gateway

What follows is a description on the hardware needed to build the MQTT SMS Gateway. I've built several - mainly using the Raspberry Pico W - but I've also used an ESP32 SoC. Expect to build these boards for around £20. Alternatively you could invest in a Raspberry Pi Zero W for £17 and buy a USB Serial GSM board for £20.

For AtoZ users - you need to be able to add more OTP numbers through the AtoZ profile section. Unfortunately, as from early 2023, the AtoZ team have made this more difficult to do as they now insist that you make these changes when connected through the Amazon secure network.


**Make sure you following these wiring instructions carefully.  It is important to avoid feeding 5v to the Pico’s GPIO pins to avoid damaging the microprocessor.**

First wire the connections between the Pico and the Buck convertor. VBUS and GND pins from the Pico is needed to go IN+ and IN- of the buck. Power you Pico and using a voltmeter check that you have 5v on these input lines.  

Using a small screw driver, adjust the buck’s variable resistor so that the voltage reading on the OUT pins on the buck read 3.7v.  The OUT+ line will be used to power the SIM800 board on its VCC line.
You should find that the IN- and OUT- are connected together -so you can use the OUT- as a convenient GND line.

You can now wire up the connections between the remaining pins on the SIM800 and the Pico board.

Next wire up your OLED display to the Pico.  The OLED display is powered from the Pico’s 3.3v pin.


Finally - wire the mode switch on the GND and GP21 pins. This mode switch is used to flip the gateway between server mode and setup mode.


The Pico version software is also included in this repository - (TODO) - with links to other materials to help you set up your device to install Micropython




![Pico MQTT SMS Gateway](/images/pico-mqtt-sms-gw.jpg)


![Pico Pins Diagram Courtesey Rasberry Pi Foundation](/images/picopins.png)

## BOM

Component|Quantity|Supplier|Approx Cost
---------|--------|--------|-----------
Raspberry Pi W Pico|1|The Pi Hut|£6.00
SSD1306 128x64 or 128x32 OLED Display|1|Amazon.co.uk|£3.00
3.7v LM2596 Buck Convertor|1|Amazon.co.uk|£3.00
Headers/Veroboard|1|AliExpress|£3.00
2 Position 3P SPDT|1|AliExpress|£1.00
5V micro USB PSU (2A/10W)|1|Various Suppliers|£3.00

Note: In the PicoW Python Source Code - Pins are usually reference by their Pico 'GP' Pin names not the Pico board pin numbers.

```
sda =Pin(14)  # OLED GP14 (Pico Pin Name)
scl =Pin(15)  # OLED GP15 (Pico Pin Name)

# SIM800 Connections
rst = Pin(26, mode=Pin.OUT, value=1) # Pull Low to reset SIM800
# TX on Pico connects to RX on SIM800, RX on Pico connects to TX on SIM800
uart = UART(0, baudrate=19200, tx=Pin(16), rx=Pin(17), timeout=500)

```

It is imperative that you build the circuit in the following order - in order to avoid 5v being fed to the Pico GPIO pin 17 from the SIM800 module.

### Task 1 - Wire Between Pico W and Buck Convertor

**Wire between Buck Convertor and Pico First -**

When the PicoW is supplied with power from a USB power supply, The voltage between VBUS and GND Pins should read around 5v.

PicoW Pin Name|PicoW Pin Number|Buck
-----|--|----
VBUS(5v)|40|IN+
GND|38*|IN-

**Adjust variable resistor on the Buck convertor (with a small screw driver) so that the voltage between OUT+ and OUT-(GND) is 3.7v**

We use this 3.7v output to feed the SIM800 board.

### Task 2 - Wire Buck Convertor and SIM800

Buck|SIM800
-----|----
OUT+|VCC   


### Task 3 - Wire Pico W and SIM800

PicoW Pin Name|PicoW Pin Number|SIM800
-----|--|----
GP16/UART0 TX|21|RX
GP17/UART0 RX|22|TX
GP26|29|RST

### Task 4 - Wire Pico W and OLED Display

PicoW Pin Name|PicoW Pin Number|OLED Display
-----|--|----
GP14/I2C1 SDA|19|SDA
GP15/I2C1 SCL|20|SCL
3.3v|36|VCC
GND|3*|GND


### Task 5 - Wire Pico W and 2-Way switch (Mode Switch)

PicoW Pin Name|PicoW Pin Number|Switch
-----|--|----
GP21|27|Left or Right Pin
GND|28*|Middle Pin

***Pico Pins 3,8,13,18,23,28,33 and 38 are connected to a common GROUND(GND).**


**The LED and fixed 220 Ohm resistor are not needed.**


## Setting up your Pico W to run Micropython

Since our Gateway software is written in Python we have to ensure that our Pico runs the MicroPython firmware. The instructions for this can be found at https://www.raspberrypi.com/documentation/microcontrollers/micropython.html

https://projects.raspberrypi.org/en/projects/getting-started-with-the-pico/0

**MAKE SURE YOU INSTALL THE PICO W VERSION, WHICH INCLUDES WIFI CONNECTIVITY**

Once you have MicroPython on your Pico and Thonny IDE installed on your host system - you're now ready to upload and install the Pico MQTT Gatewway.


## Installing the MQTT SMS Gateway Software

After installation, with the Thonny application running, plug in your Pico with its USB cable and launch Thonny.  

TODO TODO TODO



## Setting up the MQTT Mosquitto Server

At the time of writting, the Pico MQTT Gateway already has server details for a particular MQTT Broker I set up - but those services will likely be removed by the time you come to use it and so you will to set up your own server.


Here are a few examples of free or trial MQTT services:

* HiveMQ Cloud: HiveMQ Cloud offers a free tier with a limited number of connections, data transfer, and retained messages. It's a managed MQTT broker service that can be used for IoT and real-time applications.

* Adafruit IO: Adafruit IO is an IoT platform by Adafruit that provides MQTT support. They have a free tier with certain limitations, making it a great option for hobbyists and small projects.

* CloudMQTT: CloudMQTT provides a free plan with certain restrictions. It's a cloud-hosted MQTT broker service with options to scale up if needed.

* Eclipse Mosquitto: While not a cloud service, Eclipse Mosquitto is a widely used open-source MQTT broker that you can run on your own server or cloud instance. This can be a cost-effective way to set up your MQTT server.

* IBM Watson IoT Platform: IBM Watson IoT Platform offers a free trial that includes MQTT support. It's part of the IBM Cloud and is suitable for prototyping and exploring IoT solutions.

* Google Cloud IoT Core: Google Cloud IoT Core provides a fully managed MQTT broker as part of Google Cloud's IoT services. While it may not have a permanent free tier, it often comes with free trial credits for new users.

* Amazon Web Services (AWS) IoT Core: AWS IoT Core is a managed service that supports MQTT, and it may have some free tier usage for new AWS accounts. However, the free tier has limits and is typically intended for evaluation purposes. Alternatively you can use a Free Tier Linux EC2 instance and install Mosquitto MQTT Broker mentioned above. Amazon have recently (October 2023) started to charge for a public IPV4 address, but the Python MQTT libraries can handle IPV6 addressing.



If you're installing Mosquitto at home you'll need to open up relevant ports on your router and forward traffic to your home MQTT broker. Refer to your router documentation for more details. There are plenty of examples of setting up a broker on a Raspberry Pi and Docker systems.









# Alternative Versions (ESP32 SoC)
 
![Seedo MQTT SMS Gateway](/images/seeed-mqtt-sms-gw-annotate.jpg)


* Seeed XIAO ESP32C3 System-On-Chip - with WiFi £5.00
* GSM SIM800 Module £4.00
* OLED Display £2.00
* Buck Convertor 5v to 3.7v £2.00
* Veroboard, Wire, LED, 300 Ohm Resistor £2.00


Ignore the very large capacitor on the GSM module. I soldered this so that the board could provide larger than normal current draws when the board was operating from a TTL (5v) source.
Since we are running the board at 3.7v there is no need to make sure modification.

