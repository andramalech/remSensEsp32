import wifimgr
from machine import Pin, ADC
from time import sleep
import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
esp.osdebug(None)
import gc
gc.collect()

#Wireless Manager/////////////////////////////////////////////////////////////////////////
try:
  import usocket as socket
except:
  import socket

wlan = wifimgr.get_connection()
if wlan is None:
    print("Could not initialize the network connection.")
    while True:
        pass  # you shall not pass :D

# Main Code goes here, wlan is a working network.WLAN(STA_IF) instance.
print("ESP OK")

# Wireless Manager/////////////////////////////////////////////////////////////////////////


##MQTT##

#ssid = 'SSID Here'
#password = 'Password Here'

mqtt_server = 'dameant.com' # Change to your mqtt broker ip
user = 'sensor'
password = 'Tseind1'

client_id = ubinascii.hexlify(machine.unique_id()) # cookie code use the board hardware id to diff the sensor

# Define the topics here

topic_pub_temp = b'eng/remSen_%s/temperature' % client_id
topic_pub_bat = b'eng/remSen_%s/bat' % client_id

last_message = 0
message_interval = 5 # After dev lets change this to 60 second message interval

#station = network.WLAN(network.STA_IF)

#station.active(True)
#station.connect(ssid, password)

#while station.isconnected() == False:
#  pass

print('Connection successful')

# Dont forget to initialize the pins before the loop

sensor = ADC(Pin(36))
sensor.atten(ADC.ATTN_11DB)
bat = ADC(Pin(35))
bat.atten(ADC.ATTN_11DB)


def connect_mqtt():
  global client_id, mqtt_server
  #client = MQTTClient(client_id, mqtt_server)
  client = MQTTClient(client_id, mqtt_server, user, password)
  client.connect()
  print('Connected to %s MQTT broker' % (mqtt_server))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

def read_sensor():
  try:
    # temp Section Nathan put the code here to read your sensor make sure that you return the converted value as 'temp'
    #//////////////////////////////////////////////////////////////////////////////////////
    temp = sensor.read() # setup using the analog in pin with a pot on pin 36 (A4) ADC Count
    temp = (temp*20)/4095 #convert to mA

    #//////////////////////////////////////////////////////////////////////////////////////
    #temp = temp * (9/5) + 32.0  i threw this in 'cause you know i like merica!

    # battery voltage section, We need to set an alarm in ignition around 3.4v, 3.2v auto shutdown
    measuredvbat = bat.read()  # Read the value
    measuredvbat /= 4095  # divide by 4095 as we are using the default ADC voltage range of 0-1V
    measuredvbat *= 2  # Voltage is halved by the voltage divider
    measuredvbat *= 3.3 # Multiply by 3.3V, our reference voltage
    measuredvbat *= 1.1 # ADC Reference voltage is 1100mV
    batv = measuredvbat

    return temp, batv #return som n to get som n


  except OSError as e:
    return('Failed to read sensor.')

try:
  client = connect_mqtt()
except OSError as e:
  restart_and_reconnect()

while True:
  try:
    if (time.time() - last_message) > message_interval:
      temp, batv = read_sensor()
      print(temp)
      print(batv)
      client.publish(topic_pub_temp, '%s' % temp)
      client.publish(topic_pub_bat, '%s' %  batv)
      last_message = time.time()
  except OSError as e:
    restart_and_reconnect()

# Still need to work on a deep sleep to preserve battery life. I'm thinking of dropping to  low power for 60 sec.
