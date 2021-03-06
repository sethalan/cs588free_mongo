# CS588 Final project
# Seth Seeman
# Spring 2020
#
# test db connection script

import pymongo, sys
from pprint import pprint
import pandas as pd

try:
    ip = "35.236.54.92"
    #ip = sys.argv[1]
except:
    print("Must provide DB IP-Address as first argument")
    exit(1)

usr = "root"
psswrd = " "

client = pymongo.MongoClient("mongodb://" + usr + ":" + psswrd + "@" + ip + ":27017/")
db = client.freemonster
print ("\n###############################################")
#print ("#---------------------------------------------#\n")
# print all loopdata - for testing/verification
#query = {"stationid":'1047'}
#readings = db.loopdata.find()#query)
#for reading in readings:
    #print(reading)
    
count = db.loopdata.count()
print("Total Loopdata Readings: " + str(count))
count = db.detectors.count()
print("Known Detectors: " + str(count))
count = db.loopdata.distinct("detectorid")
print("Found Detectors: " + str(len(count)) + " " + str(count))
count = db.stations.count()
print("Known Stations: " + str(count))
count = db.loopdata.distinct("stationid")
print("Found Stations: " + str(len(count)) + " " + str(count))
count = db.highways.count()
print("Known Highways: " + str(count))
count = db.loopdata.distinct("highwayid")
print("Found Highways: " + str(len(count)) + " " + str(count) + '\n')
    
print ("#---------------------------------------------#")
# QUERY 1 - Count high speeds: Find the number of speeds > 100 in the data set.
print("Query 1")
reading_count = db.loopdata.count_documents({"speed": {"$gt": 100}})
print("Count of 100+ speeds: " + str(reading_count))

print ("#---------------------------------------------#")
# QUERY 2 - Volume: Find the total volume for the station Foster NB for Sept 21, 2011.
print("Query 2")
# find station id for Foster NB
station_text = "Foster NB"
query = {"locationtext": station_text}
results = db.stations.find_one({"locationtext": station_text}, {"stationid" : 1})
station =  results['stationid']
date = '2011-09-21'
# query all loopdata for station id and for sept 21, 2011 - return volume 
readings = db.loopdata.find({"stationid": station, "date": date},{"volume" : 1})
total = 0
for reading in readings:
    if reading['volume'] != '':
        # sum volumes
        total += int(reading['volume'])
print ("Station: " + station_text + " (ID: " + str(station) + ")")
print("Date: " + date)
print("Volume: " + str(total))

print ("#---------------------------------------------#")
# QUERY 3 - Single-Day Station Travel Times: Find travel time for station Foster NB for 5-minute intervals for Sept 22, 2011. 
# Report travel time in seconds.
print("Query 3")

class bucket():
    def __init__(self, intvl):
        self.intvl = intvl
        self.spdSum = 0
        self.counter = 0

spdBuckets = []  #24hours x 12 interval buckets to accummulate speeds
intvlList = []  #list of all time intervals

#set up spdBuckets array
intvls = pd.timedelta_range(0, periods = 288, freq='5Min')
for i in intvls:
    intvl = str(i)[7:12]
    spdBuckets.append(bucket(intvl))

#find stationid for "Foster NB"
query = {"locationtext": "Foster NB"}
detectors = db.detectors.find_one(query)
stationNum = detectors['stationid']
# find station length
query2 = {"stationid": stationNum}  
station = db.stations.find_one(query2)
length = station['length']
# set date 
date = '2011-09-22'

cur = 0  #current bucket
#query all loopdata for station id and for sept 22, 2011
readings = db.loopdata.find({"stationid": stationNum, "date": date}).sort("time")
for reading in readings:
    timestamp = str(reading['time'])[:5]  #the timestamp, as read
    roundedTime = None
    #round timestamp to the nearest interval
    if int(timestamp[4]) >= 0 and int(timestamp[4]) < 5:
        roundedTime = timestamp[:4] + '0'
    else:
        roundedTime = timestamp[:4] + '5'

    if reading['speed'] != '':
        #find the correct bucket to add the speed to -- since timestamps are sorted, no need to start over from 0 each time
        while spdBuckets[cur].intvl != roundedTime:
            cur += 1
        #can't simply add speed and increment counter by 1; must add speed x volume to properly calculate avg
        spdBuckets[cur].spdSum += (int(reading['speed']) * int(reading['volume']))
        spdBuckets[cur].counter += int(reading['volume'])

#calculate averages for each bucket
for bucket in spdBuckets:
    if bucket.counter > 0:
        avgSpd = bucket.spdSum / bucket.counter
        time = (length / avgSpd) * 3600
        intvlList.append(tuple((bucket.intvl, round(time,4))))
    #if no volume recorded for current interval
    else:
        intvlList.append(tuple((bucket.intvl, 'no readings')))

#print intervals and times
print ("Station: Foster NB (ID: " + str(stationNum) + ")")
print("Date: " + date)
print("Interval,  Travel Time")
for intvl in intvlList:
    if intvl[1] != 'no readings':
        print(intvl[0], "     {:0.3f}".format(intvl[1]))
    else:    
        print(intvl[0], "    ", intvl[1])

print ("#---------------------------------------------#")
# QUERY 4 - Peak Period Travel Times: Find the average travel time for 7-9AM and 4-6PM on September 22, 2011 for station Foster NB. 
# Report travel time in seconds.
print("Query 4")

location = {"locationtext": "Foster NB"}
detectors = db.detectors.find_one(location)
stationID = detectors['stationid']

station = {"stationid": stationID}  
stations = db.stations.find_one(station)
stationLength = stations['length']

windowPreLower = '05:00:00-07'
windowPreUpper = '07:00:00-07'
countPre = 0

window1Lower = '07:00:00-07'
window1Upper = '09:00:00-07'
count1 = 0

windowMiddle1Lower = '09:00:00-07'
windowMiddle1Upper = '11:00:00-07'
countMiddle1 = 0

windowMiddle2Lower = '14:00:00-07'
windowMiddle2Upper = '16:00:00-07'
countMiddle2 = 0

window2Lower = '16:00:00-07'
window2Upper = '18:00:00-07'
count2 = 0

windowPost1Lower = '18:00:00-07'
windowPost1Upper = '20:00:00-07'
countPost1 = 0

windowPost2Lower = '22:00:00-07'
windowPost2Upper = '24:00:00-07'
countPost2 = 0

def calculateAverage(windowLower, windowUpper, stationLength, count): 
    speeds = 0

    readings = db.loopdata.find({
        "stationid": stationID,
        "date": '2011-09-22',
        "time": {
            "$gte": windowLower,
            "$lte": windowUpper
        }
    })

    for reading in readings:
        if reading['speed'] is not '':
            speeds += (reading['speed'] * reading['volume'])
            count += reading['volume']
            
    if count <= 0:
        return 0
        
    return (stationLength/(speeds/count)) * 3600

averagePre = round(calculateAverage(windowPreLower, windowPreUpper, stationLength, countPre), 2)
average1 = round(calculateAverage(window1Lower, window1Upper, stationLength, count1), 2)
averageMiddle1 = round(calculateAverage(windowMiddle1Lower, windowMiddle1Upper, stationLength, countMiddle1), 2)
averageMiddle2 = round(calculateAverage(windowMiddle2Lower, windowMiddle2Upper, stationLength, countMiddle2), 2)
average2 = round(calculateAverage(window2Lower, window2Upper, stationLength, count2), 2)
averagePost1 = round(calculateAverage(windowPost1Lower, windowPost1Upper, stationLength, countPost1), 2)
averagePost2 = round(calculateAverage(windowPost2Lower, windowPost2Upper, stationLength, countPost2), 2)

print(averagePre, "Is the average travel time for Foster NB from ", windowPreLower, "to", windowPreUpper)
print(average1, "Is the average travel time for Foster NB from ", window1Lower, "to", window1Upper)
print(averageMiddle1, "Is the average travel time for Foster NB from ", windowMiddle1Lower, "to", windowMiddle1Upper)
print(averageMiddle2, "Is the average travel time for Foster NB from ", windowMiddle2Lower, "to", windowMiddle2Upper)
print(average2, "Is the average travel time for Foster NB from ", window2Lower, "to", window2Upper)
print(averagePost1, "Is the average travel time for Foster NB from ", windowPost1Lower, "to", windowPost1Upper)
print(averagePost2, "Is the average travel time for Foster NB from ", windowPost2Lower, "to", windowPost2Upper)


print ("#---------------------------------------------#")
# QUERY 5 - Peak Period Travel Times: Find the average travel time for 7-9AM and 4-6PM on September 22, 2011 for the I-205 NB freeway. 
# Report travel time in minutes.
print("Query 5")

print ("#---------------------------------------------#")
# QUERY 6 - Route Finding: Find a route from Johnson Creek to Columbia Blvd on I-205 NB using the upstream and downstream fields.
print("Query 6")

startLocation = {"locationtext": "Johnson Cr NB"}
detectors = db.stations.find_one(startLocation)
startStationID = detectors['stationid']

endLocation = {"locationtext": "Columbia to I-205 NB"}
detectors = db.stations.find_one(endLocation)
endStationID = detectors['stationid']

path = []

currentStation = startStationID

while (currentStation != endStationID) and (currentStation != 0):
    currentLocation = db.stations.find_one({"stationid": currentStation})
    path.append(currentLocation['locationtext'])
    currentStation = currentLocation['downstream']

currentLocation = db.stations.find_one({"stationid": currentStation})
path.append(currentLocation['locationtext'])

print("The path from 'Johnson Cr NB' to 'Columbia to I-205 NB' is:")
print(path)

print ("#---------------------------------------------#")
print ("###############################################\n")


