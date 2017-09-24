#!/usr/bin/python
from swamptemp import swamptemp

temp1 = swamptemp.getTemperature1()
print("Fermenter 1 temperature:")
print(temp1)

temp2 = swamptemp.getTemperature2()
print("Fermenter 2 temperature:")
print(temp2)

temp, humidity = swamptemp.getAmbientTemperatureHumidity()
print("Indoor temperature:")
print(temp)

o_temp, o_humidity = swamptemp.getOutdoorTemperatureHumidity()
print("Outdoor temperature")
print(o_temp)

print("Indoor humidity")
print(humidity)
print("Outdoor humidity")
print(o_humidity)

# Save to files:
swamptemp.writeToArchive(temp, o_temp, temp1, temp2, humidity, o_humidity,
    datadir='../data')
swamptemp.writeToWebsite(temp, o_temp, temp1, temp2, humidity, o_humidity,
    filename='../temperature.js')

# Send emails if necessary:
temps = {'temp' : temp, 'o_temp' : o_temp, 'temp1' : temp1, 'temp2' : temp2}
swamptemp.sendEmail(temps, low_temp=16, high_temp=19)
swamptemp.sendOpenWindowEmail(temps, desired_temp=20, temp_diff=1)
swamptemp.sendCloseWindowEmail(temps, desired_temp=20, temp_diff=1)
