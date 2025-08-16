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
             out_temp_and_humidity_channels = [1,2]

3.  In the WeeWX configuration file, modify the `station_type` setting to use the
    WN1821 driver

           [Station]
               ...
               station_type = WN1821

4.  Restart WeeWX

         sudo systemctl restart weewx

## out_temp_and_humidity_channels reasoning explained

In my configuration i don't have any WN32 sensor, so I need to map some of multichannel sensors as outTemp and outHumidity. Because I don't have possibility to place single sensor into shade for whole day, I added logic that in out_temp_and_humidity_channels you can specify one or more channels in array and it will pick sensor with lower temperature and map it as outTemp and outHumidity. Thanks to this you can have two (or more) sensor for example one in north east and one on south west of building and it will at morning pick one on south west and in afternoon one in north east based on which one is in shade (has lower temp).
Even when you use single channel, always use array syntax! If you don't need this mapping just doesn't provide this out_temp_and_humidity_channels at all.
