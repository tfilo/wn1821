# installer for the wn1821 driver
# Copyright 2025 Tomáš Filo

from weecfg.extension import ExtensionInstaller


def loader():
    return WN1821Installer()


class WN1821Installer(ExtensionInstaller):
    def __init__(self):
        super(WN1821Installer, self).__init__(
            version="0.1",
            name='wn1821',
            description='WN1821 API driver for weewx.',
            author="Tomáš Filo",
            config={
                'Station': {
                    'station_type': 'WN1821'},
                'WN1821': {
                    'driver': 'user.wn1821',
                    'url': 'http://192.168.4.1/get_livedata_info'}},
            files=[('bin/user', ['bin/user/wn1821.py'])]
        )