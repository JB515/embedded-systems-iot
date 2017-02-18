# TIMELINE (Embedded Systems IoT Coursework)

## Environmentally-Aware Timer for a Washing Line

Attach to a washing line to start a timer for your clothes to dry which changes dynamically based on maximum wind speed and temperature. The device consists of a temperature sensor and an airflow sensor rotating on a gear motor. It sends JSON-formatted updates to a PC server every 30 seconds, which then updates the estimated the time for the clothes to dry. Also includes a rain sensor to alert the user when it is raining.

## Hardware

* Adafruit Feather HUZZAH ESP8266
* D6F-V MEMS Air Flow Sensor
* Adafruit ADS1115 4-Channel ADC Breakout
* SI7021 Temp + Humidity Sensor
* Servo Motor
* Rain Sensor

## Software

* Micropython
* Eclipse Paho MQTT

## Team Members

* Joshua Brown (@JB515)
* Tieng Ley Toh (@tiengley)
* Baron Khan (@BaronKhan)
