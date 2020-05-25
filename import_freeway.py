# CS588 Final project
# Seth Seeman
# Spring 2020
#
# script to import all freeway data csv files to new mongoDB database

import pymongo, sys, os, csv, datetime
from pprint import pprint


#-------------------------------------------------------#
def read_input():
        try:
                ip = "35.236.54.92"
                #ip = sys.argv[1]
        except:
                print("Must provide DB IP-Address as first argument")
                exit(1)
        
        try:
                data_dir = "sample_data/"
                #data_dir = sys.argv[2]
        except:
                print("Must provide data directory as second argument")
                exit(1)
        return ip, data_dir

#-------------------------------------------------------#
def db_connect(ip):
        # need to figure out how to get environment variables to do this
        user = "root"         #str(os.environ.get('USER'))
        password = "super!secret"     #str(os.environ.get('PASSWORD'))

        # connect to remote MongoDB server
        client = pymongo.MongoClient("mongodb://" + user + ":" + password + "@" + ip + ":27017/")
        # connect to database "freeway"
        db = client["freeway"]
        return db

#-------------------------------------------------------#
def import_highways(db, highway_file):
        # delete and recreate collection (OVERWRITE)
        db.highways.drop()
        highways = db["highways"]
        
        # read csv and write to MongoDB
        with open(highway_file, 'r') as csvfile:
                csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
                next(csv_reader)       # skips first line (column headers)
                for line in csv_reader:
                        # create highway dict (schema) from input line
                        highway_dict = { "highwayid" : check_int(line[0]),
                                        "shortdirection" : str(line[1]),
                                        "direction" : str(line[2]),
                                        "highwayname" : str(line[3])
                        }
                        result = highways.insert_one(highway_dict)
        # test if insertions were successful by printing collection
#        highways = db.highways.find()
#        for highway in highways:
#                print(highway)

#-------------------------------------------------------#
def import_stations(db, station_file):
        # delete and recreate collection (OVERWRITE)
        db.staions.drop()
        stations = db["stations"]
        
        # read csv and write to MongoDB
        with open(station_file, 'r') as csvfile:
                csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
                next(csv_reader)       # skips first line (column headers)
                for line in csv_reader:
                        # find reference documents
                        highway = dict(db.highways.find({"highwayid": check_int(line[1])})[0])
                        hw_ref = highway['_id']
                        # create station dict from input line
                        station_dict = { "stationid" : check_int(line[0]),
                                        "highwayid" : check_int(line[1]),
                                        "milepost" : float(line[2]),
                                        "locationtext" : str(line[3]),
                                        "upstream" : check_int(line[4]),
                                        "downstream" : check_int(line[5]),
                                        "stationclass" : check_int(line[6]),
                                        "numberlanes" : check_int(line[7]),
                                        "latlon" : str(line[8]),
                                        "length" : float(line[9]),
                                        # reference _ids 
                                        "highwayref": str(hw_ref),
                        }
                        #insert station 
                        result = stations.insert_one(station_dict) 
        # test if insertions were successful by printing collection
 #       stations = db.stations.find()
 #       for station in stations:
 #               pprint(station)
                        
#-------------------------------------------------------#
def import_detectors(db, detector_file):
        # delete and recreate collection (OVERWRITE)
        db.detectors.drop()
        detectors = db["detectors"]

        with open(detector_file, 'r') as csvfile:
                csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
                next(csv_reader)       # skips first line (column headers)
                for line in csv_reader:
                        # find reference documents
                        highway = dict(db.highways.find({"highwayid": check_int(line[1])})[0])
                        hw_ref = highway['_id']
                        station = dict(db.stations.find({"stationid": check_int(line[6])})[0])
                        st_ref = station['_id']
                        # create detector dict (schema) from input line
                        detector_dict = { "detectorid" : check_int(line[0]),
                                        "highwayid" : check_int(line[1]),
                                        "milepost" : float(line[2]),
                                        "locationtext" : str(line[3]),
                                        "detectorclass" : check_int(line[4]),
                                        "lanenumber" : check_int(line[5]),
                                        "stationid" : check_int(line[6]),
                                        # reference _ids 
                                        "stationref": str(st_ref),
                                        "highwayref": str(hw_ref)
                                        # this might be the more correct way of referencing, 
                                        # if we figure out how to query this format (ObjectId function not in pymongo)
                                        #"highwayref": { "$ref": "highway", "$_id": ObjectId(str(hw_ref)) } 
                        }
                        result = detectors.insert_one(detector_dict)
        # test if insertions were successful by printing collection
 #       detectors = db.detectors.find()
 #       for detector in detectors:
 #               print(detector)
 
 #-------------------------------------------------------#
def import_loopdata(db, loopdata_file):
        # delete and recreate collection (OVERWRITE)
        db.loopdata.drop()
        loopdata = db["loopdata"]

        with open(loopdata_file, 'r') as csvfile:
                csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
                next(csv_reader)       # skips first line (column headers)
                
                # use i counter to limit number of imports for testing
                i = 0
                for line in csv_reader:
                        # find reference documents
                        detector = dict(db.detectors.find({"detectorid": check_int(line[0])})[0])
                        dt_ref = detector['_id']
                        hw_ref = detector['highwayref']
                        st_ref = detector['stationref']
                        # create reading dict (schema) from input line
                        reading_dict = { "detectorid" : check_int(line[0]),
                                        # probably need to figure our datetime formatting in Mongo
                                        "starttime" : str(line[1]),
                                        "volume": check_int(line[2]), 
                                        "speed" : check_int(line[3]),
                                        "occupancy" : check_int(line[4]),
                                        "status" : check_int(line[5]),
                                        "dqflags" : check_int(line[6]),
                                        # reference _ids 
                                        "detectorref" : str(dt_ref),
                                        "stationref": str(st_ref),
                                        "highwayref": str(hw_ref)
                        }
                        result = loopdata.insert_one(reading_dict)
                        i += 1
                        print(i)
                        # limit number of imports for testing
                        if i > 100:
                                break
        # test if insertions were successful by printing collection
        loopdata = db.loopdata.find()
        for reading in loopdata:
                pprint(reading)
#-------------------------------------------------------#
# utility function to check if input_string is 
# null before converting to integer
def check_int(input_string):
        if input_string == '':
                return str('')
        else:
                return int(input_string)


#########################################################
#---------------------MAIN------------------------------#
def main():
        # get ip and data directory path from either
        # environment variables, command line input or
        # hard coded for testing
        ip, data_dir = read_input()
        # connect to MongoDB 
        db = db_connect(ip)
        # set input file paths 
        detector_file = data_dir + "/detectors.csv"
        station_file = data_dir + "/stations.csv"
        highway_file = data_dir + "/highways.csv"
        loopdata_file = data_dir + "/freeway100k_sample.csv"
        # import data into MongoDB collections from csv files
        import_highways(db, highway_file)
        import_stations(db, station_file)
        import_detectors(db, detector_file)
        import_loopdata(db, loopdata_file)
        
        exit(0)
  

if __name__ == "__main__":
    main()
