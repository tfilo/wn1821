# WN1821 - driver that reads data from Ecowitt WN1821 using http api

Copyright 2025 Tomáš Filo

## Installation instructions using the installer (recommended)

1.  Install the extension.

    For pip installs:

         weectl extension install ~/wn1821

    For package installs

         sudo weectl extension install ~/wn1821

2.  Select the driver.

    For pip installs:

         weectl station reconfigure

    For package installs:

         sudo weectl station reconfigure

3.  Restart WeeWX

         sudo systemctl restart weewx

## Manual installation instructions

1.  Copy the wn1821 driver to the WeeWX user directory.

    For pip installs:

         cd ~/wn1821
         cp bin/user/wn1821.py ~/etc/weewx-data/bin/user

    For package installs:

         cd ~/wn1821
         sudo cp bin/user/wn1821.py /usr/share/weewx/user

2.  Add a new `[WN1821]` stanza to the WeeWX configuration file

        [WN1821]
             driver = user.wn1821
             url = http://192.168.4.1/get_livedata_info
             out_temp_and_humidity_channels = 1,2

3.  In the WeeWX configuration file, modify the `station_type` setting to use the
    WN1821 driver

           [Station]
               ...
               station_type = WN1821

4.  Restart WeeWX

         sudo systemctl restart weewx

## out_temp_and_humidity_channels reasoning explained

In my configuration i don't have any WN32 sensor, so I need to map some of multichannel sensors as outTemp and outHumidity. Because I don't have possibility to place single sensor into shade for whole day, I added logic that in out_temp_and_humidity_channels you can specify one or more channels in comma separated list and it will pick sensor with lowest temperature and map it as outTemp and outHumidity. This allow place multiple sensors on different sides building and it will pick always one in shade (or at least one with coldest temperature).
