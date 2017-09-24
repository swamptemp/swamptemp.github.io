# -*- coding: utf-8 -*-
import sys
import dht11
import datetime, os, re, smtplib, time 
import json
from time import strftime
import RPi.GPIO as GPIO
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests

class swamptemp:
    # Get the ambient temperature and humidity
    @staticmethod
    def getAmbientTemperatureHumidity():
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup()
        instance = dht11.DHT11(pin=17)
        counter = 0
        temps = []
        humidities = []
	while counter < 10:
            time.sleep(1)
            result = instance.read()
            if result.is_valid():
                temps.append(result.temperature)
                humidities.append(result.humidity)
            else:
                counter += 1
        temp = sum(temps) / float(len(temps))
        humidity = round(sum(humidities) / float(len(humidities)), 2)
        return temp, humidity

    # Get the outside temperature
    @staticmethod
    def getOutdoorTemperatureHumidity():
        root_url = 'https://api.forecast.io/forecast/'
        f = open('/home/pi/.forecast-io-key')
        key = f.readline().rstrip()
        f.close()
        lat = '42.366'
        lon = '-71.115'
        weather = requests.get(root_url + key + '/' + lat + ',' + lon)
        weather = json.loads(weather.text)
        temp = round((weather['currently']['temperature']-32) * 5/9, 2)
        humidity = weather['currently']['humidity'] * 100
        return temp, humidity
    
    # Read the temperature from probe 1:
    @staticmethod
    def getTemperature1():
 	f = list(open('/sys/bus/w1/devices/28-0416a173a8ff/w1_slave', 'r'))
	temp = re.sub('t=', '', re.findall('t=[0-9]+$', str(f[1]))[0])
	temp = float(temp) / 1000.0	
        return temp

    # Read the temperature from probe 2:
    @staticmethod
    def getTemperature2():
 	f = list(open('/sys/bus/w1/devices/28-0516850c71ff/w1_slave', 'r'))
	temp = re.sub('t=', '', re.findall('t=[0-9]+$', str(f[1]))[0])
	temp = float(temp) / 1000.0	
        return temp

    # Create the website:
    @staticmethod
    def writeToWebsite(temp, o_temp, temp1, temp2, humidity, o_humidity, filename):
        text = 'document.write(\"<h4>Inside Temperature: '
        text += str(round(temp, 2)) + '°C</h4>'
        text += '<h4>Outside Temperature: '
        text += str(round(o_temp, 2)) + '°C</h4>'
        text += '<h4>Fermenter 1 Temperature: '
        text += str(round(temp1, 2)) + '°C</h4>'
        text += '<h4>Fermenter 2 Temperature: '
        text += str(round(temp2, 2)) + '°C</h4>'
        text += '<h4>Inside Humidity: '
        text += str(round(humidity, 2)) + '%</h4>'
        text += '<h4>Outside Humidity: '
        text += str(round(o_humidity, 2)) + '%</h4><br>Last update: '
        text += datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        text += '\");'
        with open(filename, "w") as f:
            f.write(text)
        return 0

    # Save all temperature readings from a day into a file:
    @staticmethod
    def writeToArchive(temp, o_temp, temp1, temp2, humidity, o_humidity, datadir):
        if datadir[-1] != '/':
            datadir += '/'
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ymd = datetime.datetime.now().strftime('%Y-%m-%d')
        ym = datetime.datetime.now().strftime('%Y-%m')
        if not os.path.exists(datadir + ym):
            os.makedirs(datadir + ym)
        filepath = datadir + ym + '/' + ymd + '.csv'
        with open(filepath, "a") as f:
            f.write(current_time + ',' +
                str(temp) + ',' +
                str(o_temp) + ',' +
                str(temp1) + ',' +
                str(temp2) + ',' +
                str(humidity) + ',' +
                str(o_humidity) + '\n')
        f.close()

    # Send an email if outside the range
    @staticmethod
    def sendEmail(temps, low_temp, high_temp):
        with open ('/home/pi/swamptemp.github.io/state/fermenter', 'r') as f:
            old_state = f.read().replace('\n', '')
        max_temp = [temps['temp1'] if temps['temp1'] > temps['temp2']
                else temps['temp2']][0]
        min_temp = [temps['temp1'] if temps['temp1'] < temps['temp2']
                else temps['temp2']][0]
        if min_temp < low_temp:
            new_state = 'cold'
        elif max_temp > high_temp:
            new_state = 'hot'
        else:
            new_state = 'ok'
        if new_state != old_state:
            with open ('/home/pi/swamptemp.github.io/state/fermenter', 'w') as f:
                f.write(new_state)
            emails = {
                'Christoph' : 'criostoir' + 'breathnach' + '@gmail.com',
                'Roisin' : 'roisin' + 'donnellyireland' + '@gmail.com'
            }
            with open ('/home/pi/.config/.email', 'r') as f:
                pswd = f.read().replace('\n', '')
            for i in range(len(emails)):
                server = smtplib.SMTP('smtp.bu.edu:587')
                server.starttls()
                server.login("walshcb@bu.edu", pswd)
                message = MIMEMultipart()
                message['From'] = 'Swamp Cooler <swamp@cooler.com>'
                receiver = list(emails.keys())[i]
                message['To'] = receiver + '<' + emails[receiver] + '>'
                if min_temp < low_temp:
                    message['Subject'] = 'Fermenter Temperature Too Low'
                elif max_temp > high_temp:
                    message['Subject'] = 'Fermenter Temperature Too High'
                else:
                    message['Subject'] = 'Fermenter Temperature Okay'
                body = 'Hello ' + receiver + ',\n\n'
                body += 'The current temperatures are '
                body += str(round(temps['temp1'], 2))
                body += ' and '
                body += str(round(temps['temp2'], 2))
                body += '\n\n'
                if min_temp < low_temp:
                    body += 'Add some hot water.'
                elif max_temp > high_temp:
                    body += 'Add some ice.'
                else:
                    body += 'All is well.'
                body += '\n\nBest,'
                body += '\n\n🐍'
                message.attach(MIMEText(body, 'plain'))
                server.sendmail('walshcb@bu.edu', emails[receiver], message.as_string())
                server.quit()

    # Send an email if outside temperature is less than inside:
    @staticmethod
    def sendOpenWindowEmail(temps, desired_temp, temp_diff):
        with open ('/home/pi/swamptemp.github.io/state/window', 'r') as f:
            window_state = f.read().replace('\n', '')
        if temps['temp'] > temps['o_temp'] + temp_diff and \
            temps['temp'] > desired_temp and window_state == 'closed':
            emails = {
                'Christoph' : 'criostoir' + 'breathnach' + '@gmail.com',
                'Roisin' : 'roisin' + 'donnellyireland' + '@gmail.com'
            }
            with open ('/home/pi/.config/.email', 'r') as f:
                pswd = f.read().replace('\n', '')
            for i in range(len(emails)):
                server = smtplib.SMTP('smtp.bu.edu:587')
                server.starttls()
                server.login("walshcb@bu.edu", pswd)
                message = MIMEMultipart()
                message['From'] = 'Banks Street Weather Man <windows@banksstreet.com>'
                receiver = list(emails.keys())[i]
                message['To'] = receiver + '<' + emails[receiver] + '>'
                message['Subject'] = 'Open windows'
                body = 'Hello ' + receiver + ',\n\n'
                body += 'The current temperature in Banks Street is '
                body += str(round(temps['temp'], 2))
                body += '°C while outside it is '
                body += str(round(temps['o_temp'], 2))
                body += '°C.'
                body += '\n\nYou should probably open the windows.'
                body += '\n\nBest,'
                body += '\n\n🐍'
                message.attach(MIMEText(body, 'plain'))
                server.sendmail('walshcb@bu.edu', emails[receiver], message.as_string())
                server.quit()
            with open('/home/pi/swamptemp.github.io/state/window', 'w') as f:
                f.write('open')

    # Send an email if inside temperature is less than outside:
    @staticmethod
    def sendCloseWindowEmail(temps, desired_temp, temp_diff):
        with open ('/home/pi/swamptemp.github.io/state/window', 'r') as f:
            window_state = f.read().replace('\n', '')
        if temps['temp'] < temps['o_temp'] - temp_diff and \
            temps['temp'] > desired_temp and window_state == "open":
            emails = {
                'Christoph' : 'criostoir' + 'breathnach' + '@gmail.com',
                'Roisin' : 'roisin' + 'donnellyireland' + '@gmail.com'
            }
            with open ("/home/pi/.config/.email", "r") as f:
                pswd = f.read().replace('\n', '')
            for i in range(len(emails)):
                server = smtplib.SMTP('smtp.bu.edu:587')
                server.starttls()
                server.login("walshcb@bu.edu", pswd)
                message = MIMEMultipart()
                message['From'] = 'Banks Street Weather Man <windows@banksstreet.com>'
                receiver = list(emails.keys())[i]
                message['To'] = receiver + '<' + emails[receiver] + '>'
                message['Subject'] = 'Close windows'
                body = 'Hello ' + receiver + ',\n\n'
                body += 'The current temperature in Banks Street is '
                body += str(round(temps['temp'], 2))
                body += '°C while outside it is '
                body += str(round(temps['o_temp'], 2))
                body += '°C.'
                body += '\n\nYou should probably close the windows if they are open.'
                body += '\n\nBest,'
                body += '\n\n🐍'
                message.attach(MIMEText(body, 'plain'))
                server.sendmail("walshcb@bu.edu", emails[receiver], message.as_string())
                server.quit()
            with open('/home/pi/swamptemp.github.io/state/window', 'w') as f:
                f.write('closed')
