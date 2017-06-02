## Read temperature via DS18B20 and RPI and send values via HTTP in JSON-format to SQL Server
##
## Temeparture values is read from DS18B20 by modprobe (https://en.wikipedia.org/wiki/Modprobe) in Linux. 
## Values are stored in /sys/bus/w1/devices/<devicename>/w1_slave
## Main loop wait's 10 sec and send's av POST in JSON to be9.asuscomm.com//proj/templog/index.asp:80

import httplib
import urllib
import os
import glob
import time

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def printText(txt):
    lines = txt.split('\n')
    for line in lines:
        print line.strip()

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f

def read_c_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c


while True:
	print read_c_temp()
	temp_value = read_c_temp()
	time.sleep(1 * 10) #vanta x sekunder
	#https://docs.python.org/release/2.7/library/httplib.html#examples

	params = urllib.urlencode({'temp': temp_value, 'user': 'johan', 'token': '1bb03973-65c2-468d-9123-c331214200dc' })
	headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

	conn = httplib.HTTPConnection("be9.asuscomm.com", 80)
	conn.connect()

	conn.request('POST', '/proj/templog/index.asp', params, headers)

    #output response
	#response = conn.getresponse()
	#if response.status == httplib.OK:
	    #print "Output from ASP request"
	    #printText (response.read())

	conn.close()
