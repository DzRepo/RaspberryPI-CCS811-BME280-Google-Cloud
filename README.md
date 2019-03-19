# RaspberryPI conected CCS811/BME280 to Google Cloud

## Purpose

Gathers environmental data:

* Temperature
* Humidity
* Pressure
* DewPoint (calculated)
* Total Volitile Organic Compounds
* Estimated CO<sub>2</sub> 

from a Raspberry Pi connected [Sparkfun Environmental Combo Breakout](https://www.sparkfun.com/products/14348) and pushes it to Google Cloud via Pub/Sub, and stores the data in BigQuery

This project is based on the Google Codelab:[*Building a Serverless Data Pipeline: IoT to Analytics*](https://codelabs.developers.google.com/codelabs/iot-data-pipeline/index.html#0)

It was expanded to include the storage of the additional fields available with the CSS811 sensor.

## Output
Besides a SQL table full of data, you can easily make charts to track changes, trends, etc. with Google DataStudio:

![Chart](https://github.com/DzRepo/RaspberryPI-CCS811-BME280-Google-Cloud/blob/master/Screenshot-Environmental%20Monitor-Chart-Hourly.png)

## Requirements
Libraries:
adafruit_bme280:
```sudo pip3 install adafruit-circuitpython-bme280```

*(I had better luck with this library than the codelab method)*

And the css811 python library found here:
[`https://github.com/sparkfun/CCS811_Air_Quality_Breakout`](https://github.com/sparkfun/CCS811_Air_Quality_Breakout)

It also requires the pigpiod service to be running:

```
sudo systemctl enable pigpiod
sudo systemctl start pigpiod 
```
Also, the I2C baud rate needs to be lowered as described here:

[`https://learn.adafruit.com/adafruit-ccs811-air-quality-sensor/raspberry-pi-wiring-test`](https://learn.adafruit.com/adafruit-ccs811-air-quality-sensor/raspberry-pi-wiring-test)

To push data to Google Cloud, you'll need:

Tendo: ```pip install tendo```

Pub/Sub: ```pip install --upgrade google-cloud-pubsub```

oauth2 client: ```sudo pip install --upgrade oauth2client```

Error Reporting: ```pip install google-cloud-error-reporting```

*(follow the codelab for the best instructions on installing google bits & connecting to the pub/sub points!)*

The BigQuery table schema is [sensorDataTable.json](). The modifications allow for the extra fields for storing eco<sub>2</sub> and tvoc.

[`https://cloud.google.com/bigquery/docs/schemas#using_a_json_schema_file`](https://cloud.google.com/bigquery/docs/schemas#using_a_json_schema_file) shows how to create the table using this file.

Ping me on Twitter [@SteveDz](https://twitter.com/stevedz) if you have any questions.
