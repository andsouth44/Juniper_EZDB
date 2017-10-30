## EZDB

This application has 2 parts.

create_device_db_production.py does the following:

* Creates an SQLite3 database
* Connects to all the devices in a supplied device list
* Retrieves information from each device
* Places the information from each device in the database

DBInterface_V1.1.py does the following:

* Connects to the server where the database is located
* Downloads a copy of the database to the local device
* Provides a TKInter GUI to retrieve information from the database

### Prerequisites server
* SQLite3
* Python2.7
* Juniper PyEZ

### Prerequisites pc
* TKInter
* Python2.7

### Set Up
* Locate a server with access to all the network devices.
* Install the prerequisites on the server.
* Fill in the variables in the files in locations marked with INSERT.
* Run create_device_db_production.py to create database
* Optional - Set up crontab to run create_device_db_production.py at regular times
* Install the prerequisites on your device
* Copy DBInterface_V1.1 to your Python2.7 files 
* Run DBInterface_V1.1.py on your device to start GUI and view database.


### Author and License

andsouth44@gmail.com

EZDB is released under the [MIT License](License.txt)
