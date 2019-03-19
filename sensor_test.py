import board
import digitalio
import busio
import time
import adafruit_bme280
import ccs811 as ccs
import math
import datetime
from datetime import timedelta
from google.cloud import pubsub
from oauth2client.client import GoogleCredentials
from tendo import singleton
import sys
import json
from google.cloud import error_reporting

interval = 60 # number of seconds between readings
warmup_delay = 20 * 60 # (in seconds)- 20 minute warmup for the sensor is best practice.

# set the following four constants to be indicative of where you are placing your weather sensor
sensorID = "Plant1-NE"
sensorZipCode = "80503"
sensorLat = "40.123456"
sensorLong = "-105.11223344"

# change project to your Project ID
project="iot-analytics-pipeline-233117"

# change topic to your PubSub topic name
topic = "sensordata"

topicName = 'projects/' + project + '/topics/' + topic


def dewpoint(t_air_c, rel_humidity):
    """Compute the dew point in degrees Celsius
    :param t_air_c: current ambient temperature in degrees Celsius
    :type t_air_c: float
    :param rel_humidity: relative humidity in %
    :type rel_humidity: float
    :return: the dew point in degrees Celsius
    :rtype: float
    """
    A = 17.27
    B = 237.7
    alpha = ((A * t_air_c) / (B + t_air_c)) + math.log(rel_humidity/100.0)
    return (B * alpha) / (A - alpha)

def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor

def createJSON(id, timestamp, zip, lat, long, temperature, humidity, dewpoint, pressure, tvoc, evoc):
    json_str = ""
    try:
        data = {
          'sensorID' : id,
          'timecollected' : timestamp,
          'zipcode' : zip,
          'latitude' : lat,
          'longitude' : long,
          'temperature' : temperature,
          'humidity' : humidity,
          'dewpoint' : dewpoint,
          'pressure' : pressure,
          'tvoc' : tvoc,
          'eco2' : evoc
        }

        json_str = json.dumps(data)
    except:
        print("Error condition creating JSON payload: ", sys.exc_info()[0])

    return json_str

def report_error(error):
    # add SensorID to the error payload so the correct sensor can be identified.
    client = error_reporting.Client()
    http_context = error_reporting.HTTPContext(user_agent=sensorID)
    client.report_exception(http_context=http_context)

def main():
    me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running

    spinner = spinning_cursor()

   # Intitialize sensors
    try:
        print("Intializing BME280 Sensor")
        i2c = busio.I2C(board.SCL, board.SDA)
        bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
        bme280.sea_level_pressure = 1019.6 # 1013.25 is the standard value. Optimized by altitude, initial data from https://forecast.weather.gov/product.php?issuedby=BOU&product=OSO&site=bou
    except Exception as ex:
        print("Error intializing BME280 Sensor:", sys.exc_info()[0])
        report_error(ex)
        exit()

    try:
        print("Intializing CCS811 Sensor")
        aqm = ccs.CCS811()
        aqm.setup()
    except Exception as ex:
        print("Error intializing CCS811 Sensor:", sys.exc_info()[0])
        report_error(ex)
        exit()

    # configure Google Cloud settings
    credentials = GoogleCredentials.get_application_default()
    publisher = pubsub.PublisherClient()	

    datetimeFormat = '%Y-%m-%d %H:%M:%S.%f'
    start_time = datetime.datetime.utcnow()
    
    while True:
        current_time = datetime.datetime.utcnow()
        sensorTime = current_time.strftime('%Y-%m-%d %H:%M:%S')

        #capture BME readings
        temp = '{0:0.2f}'.format(bme280.temperature)
        humidity = '{0:0.2f}'.format(bme280.humidity)
        dew_point = '{0:0.2f}'.format(dewpoint(bme280.temperature, bme280.humidity))
        pressure = '{0:0.2f}'.format(bme280.pressure)
        altitude = '{0:0.2f}'.format(bme280.altitude) # not capturing (assuming stationary!) but displaying

        # capture CCS811 readings
        try:
            if aqm.data_available():
                aqm.read_logorithm_results()
                eco2 = aqm.CO2
                tvoc = aqm.tVOC
            elif aqm.check_for_error():
                aqm.print_error()
        except Exception as ex:
            print("Error condition detected reading CCS811 sensor: ", sys.exc_info()[0])
            report_error(ex)            

        print("\033c") # an admitedly hack way to clear the screen on a linux terminal
        print("Date - Time:", sensorTime)
        print("Temperature: %s C" % temp)
        print("   Humidity: %s rh" % humidity)
        print("   Dewpoint: %s C" % dew_point)
        print("   Pressure: %s hPa" % pressure)
        print("   Altitude: %s m" % altitude)
        print("       eCO2: %d PPM " % eco2)
        print("       tVOC: %d PPB " % tvoc)
        
        run_time = current_time - start_time
                    
        if run_time.seconds < warmup_delay:
            # elapsed_time = timedelta(run_time)
            print("Warm up mode (20 minutes) Elapsed time:", str(run_time).split('.')[0])
        else:
            print("Saving data")
            sensorJSON = createJSON(sensorID,
                                   sensorTime,
                                   sensorZipCode,
                                   sensorLat,
                                   sensorLong,
                                   temp,
                                   humidity,
                                   dew_point,
                                   pressure,
                                   str(tvoc),
                                   str(eco2)).encode('utf-8')
            
            # print("Sensor Data JSON created")
            # print("sensorJSON:", sensorJSON)

            try:
                publisher.publish(topicName, sensorJSON, placeholder='')
            except Exception as ex:
                print("Error condition detected sending sensor data: ", sys.exc_info()[0])
                report_error(ex)
                
        if run_time.seconds < warmup_delay:  #read more while warming up!
            time.sleep(2)
        else:
            print("Pausing for", interval, "seconds")
            sys.stdout.write('\033[s') # save cursor location
            while ((datetime.datetime.utcnow() - current_time).seconds) < (interval - 1):
                        
                sys.stdout.write(next(spinner) + " " + str((datetime.datetime.utcnow() - current_time).seconds)) 
                sys.stdout.flush()
                sys.stdout.write('\033[u') # move back to saved cursor location
                time.sleep(.5)

if __name__ == "__main__": main()
