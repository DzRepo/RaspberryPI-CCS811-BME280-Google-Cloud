# RaspberryPI-CCS811-BME280-Google-Cloud
Gathers data from a Raspberry Pi connected Sparkfun Environmental Combo Breakout and pushes it to Google Cloud (BigQuery)

This uses (expects to have installed) the following libraries:
adafruit_bme280:

```sudo pip3 install adafruit-circuitpython-bme280```

And the css811 python library found here:

```https://github.com/sparkfun/CCS811_Air_Quality_Breakout```

It also requires the gpoid service to be running, and the I2C baud rate to be lowered as described here:
https://learn.adafruit.com/adafruit-ccs811-air-quality-sensor/raspberry-pi-wiring-test

To talk to Google Cloud, you'll need:
Pub/Sub: ```pip install --upgrade google-cloud-pubsub```
Error Reporting: ```pip install google-cloud-error-reporting```

The BigQuery table schema is sensorDataTable.json
```https://cloud.google.com/bigquery/docs/schemas#using_a_json_schema_file``` shows how to create the table using this file.

This project is based on the Google Codelab:*Building a Serverless Data Pipeline: IoT to Analytics*
```https://codelabs.developers.google.com/codelabs/iot-data-pipeline/index.html#0```

