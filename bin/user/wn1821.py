# Copyright 2025 Tomáš Filo
#
# weewx driver that reads data from Ecowitt WN1821 station API
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.
#
# See http://www.gnu.org/licenses/

# To use this driver, put this file in the weewx user directory, then make
# the following changes to weewx.conf:
#
# [Station]
#     station_type = WN1821
# [WN1821]
#     driver = user.wn1821
#     url = http://192.168.4.1/get_livedata_info
#     out_temp_and_humidity_channels = 1,2 # Optional, specify channels for outdoor temperature and humidity if you have only WN31 sensors, it will pick sensor with lowest temperature, comma separated list


import logging
import requests
import time
import weewx.drivers

DRIVER_NAME = 'WN1821'
DRIVER_VERSION = "0.1"

log = logging.getLogger(__name__)

def loader(config_dict, engine):  # @UnusedVariable
    return WN1821(**config_dict[DRIVER_NAME])

class WN1821(weewx.drivers.AbstractDevice):
    """Driver for the Ecowitt WN1821 station."""

    def __init__(self, **config):
        """Initialize the driver with configuration from weewx.conf."""
        self.url = config.get('url', 'http://192.168.4.1/get_livedata_info')  # Default http://192.168.4.1/get_livedata_info if not provided
        self.out_temp_and_humidity_channels = config.get('out_temp_and_humidity_channels', None)
        if self.out_temp_and_humidity_channels is not None:
            if isinstance(self.out_temp_and_humidity_channels, str):
                # Split the string by commas and strip whitespace
                self.out_temp_and_humidity_channels = [ch.strip() for ch in self.out_temp_and_humidity_channels.split(",") if ch.strip()]
            elif isinstance(self.out_temp_and_humidity_channels, int):
                # Convert a single number to a list
                self.out_temp_and_humidity_channels = [str(self.out_temp_and_humidity_channels)]
            # If the resulting list is empty, set it to None
            if not self.out_temp_and_humidity_channels:
                self.out_temp_and_humidity_channels = None
        else:
            # Keep None if no channels are specified
            self.out_temp_and_humidity_channels = None
        log.info(f"WN1821 driver initialized with:\n"
         f"  URL: {self.url}\n"
         f"  Out Temp and Humidity Channels: {self.out_temp_and_humidity_channels}")

    @property
    def hardware_name(self):
        return DRIVER_NAME
    
    def genLoopPackets(self):
        """Main generator function that continuously returns loop packets
        weewx api to return live records.""" 

        log.debug('genLoopPackets() getting live info')

        while True:
            try:
                # Perform HTTP GET request to fetch data
                response = requests.get(self.url, timeout=10)
                response.raise_for_status()  # Raise an exception for HTTP errors
                data = response.json()

                # Parse the JSON data
                _packet = {}

                # Extract indoor data (wh25)
                if "wh25" in data and data["wh25"]:
                    wh25 = data["wh25"][0]
                    _packet["inTemp"] = float(wh25["intemp"])
                    _packet["inHumidity"] = int(wh25["inhumi"].strip('%'))
                    _packet["barometer"] = float(wh25["rel"].split()[0])  # Relative pressure
                    _packet["pressure"] = float(wh25["abs"].split()[0])  # Absolute pressure
                    _packet["co2"] = float(wh25["CO2"])  # CO2 level

                # Extract channel data (ch_aisle)
                if "ch_aisle" in data:
                    for channel in data["ch_aisle"]:
                        channel_number = channel["channel"]
                        if channel_number not in [str(i) for i in range(1, 9)]:  # Allow only channels 1 to 8
                            log.warning(f"Ignoring invalid channel: {channel_number}")
                            continue
                        _packet[f"extraTemp{channel_number}"] = float(channel["temp"])
                        _packet[f"extraHumid{channel_number}"] = int(channel["humidity"].strip('%'))
                        _packet[f"batteryStatus{channel_number}"] = float(channel["battery"])
                    
                    # Calculate outdoor temperature and humidity from choosen channels
                    if self.out_temp_and_humidity_channels is not None:
                        # Find the channel with the lowest temperature
                        lowest_temp_channel = None
                        lowest_temp = float("inf")

                        for channel in data["ch_aisle"]:
                            if channel_number not in [str(i) for i in range(1, 9)]:  # Allow only channels 1 to 8
                                log.warning(f"Ignoring invalid channel: {channel_number}")
                                continue
                            if channel["channel"] in self.out_temp_and_humidity_channels:
                                temp = float(channel["temp"])
                                if temp < lowest_temp:
                                    lowest_temp = temp
                                    lowest_temp_channel = channel

                        # Map the lowest temperature channel to outTemp and outHumidity
                        if lowest_temp_channel:
                            _packet["outTemp"] = float(lowest_temp_channel["temp"])
                            _packet["outHumidity"] = int(lowest_temp_channel["humidity"].strip('%'))         

                # Add a timestamp
                _packet["dateTime"] = int(time.time())
                _packet["usUnits"] = weewx.METRIC  # Use METRIC units

                log.debug(f"Generated packet: {_packet}")

                # Yield the packet
                yield _packet

            except requests.exceptions.RequestException as e:
                log.error(f"Error fetching data from WN1821: {e}")
            except Exception as e:
                log.error(f"Error processing data: {e}")

            # Sleep for the desired interval (e.g., 60 seconds)
            # Keep at least one minute to prevent calling api too often
            time.sleep(60)


# To test this driver, run it directly as follows:
#   PYTHONPATH=/home/weewx/bin python /home/weewx/bin/user/wn1821.py
if __name__ == "__main__":
    import weeutil.weeutil
    import weeutil.logger
    import weewx

    weewx.debug = 1
    weeutil.logger.setup('wn1821')

    driver = WN1821()
    for packet in driver.genLoopPackets():
        print(weeutil.weeutil.timestamp_to_string(packet['dateTime']), packet)