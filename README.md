# remSens Huzzah 32

This is for the Huzzah 32.
Provisions for wireless setup using an access point@192.168.1.4 
Mqtt publish to broker
 * sensor
 * battery voltage
 * I am using the esp hardware id in the topic path so this code is vanilla for all micropython boards with wifi.
 
Nathan i left a section in the main.py code for you to add your sensor module code. ensure that you return the formatted value as `temp`
