# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ipmisim - Fake IPMI simulator for testing, forked from Conpot
# Maintainer - Rohit Yadav <bhaisaab@apache.org>
# Original Author: Peter Sooky <xsooky00@stud.fit.vubtr.cz>
# Brno University of Technology, Faculty of Information Technology

import logging
import os
import sys
from pyghmi.ipmi.bmc import Bmc

import packet

logger = logging.getLogger('fakebmc')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

METAL_AUTH_TOKEN = os.getenv("METAL_AUTH_TOKEN")
METAL_SERVER_UUID = os.getenv("METAL_SERVER_UUID")
if METAL_AUTH_TOKEN is None:
    logger.error("OS ENV variable METAL_AUTH_TOKEN= must be set")
    sys.exit(1)
elif METAL_SERVER_UUID is None:
    logger.error("OS ENV variable METAL_SERVER_UUID= must be set")
    sys.exit(1)

manager = packet.Manager(auth_token=METAL_AUTH_TOKEN)
server = manager.get_device(METAL_SERVER_UUID)


class FakeBmc(Bmc):

    def __init__(self, authdata):
        self.authdata = authdata
        # Initialize fake BMC config
        self.deviceid = 0x24
        self.revision = 0x10
        self.firmwaremajor = 0x10
        self.firmwareminor = 0x1
        self.ipmiversion = 2
        self.additionaldevices = 0
        self.mfgid = 0xf
        self.prodid = 0xe

        self.powerstate = 'off'
        self.bootdevice = 'default'
        logger.info('IPMI BMC initialized.')

    def get_boot_device(self):
        logger.info('IPMI BMC Get_Boot_Device request.')
        return self.bootdevice

    def set_boot_device(self, bootdevice):
        logger.info('IPMI BMC Set_Boot_Device request.')
        self.bootdevice = bootdevice

    def cold_reset(self):
        logger.info('IPMI BMC Cold_Reset request.')
        self.powerstate = 'off'
        self.bootdevice = 'default'

    def get_power_state(self):
        server = manager.get_device(METAL_SERVER_UUID)
        logger.info('IPMI BMC Get_Power_State request.')
        logger.info('Metal Server State: %s' % server.state)
        if server.state == 'active':
            self.powerstate = 'on'
        if server.state == 'powering_on':
            logger.debug('Metal Server is powering on')
            self.powerstate = 'on'
        if server.state == 'powering_off':
            logger.debug('Metal Server is powering off')
            self.poweroff = 'off'
        elif server.state == 'inactive':
            self.powerstate = 'off'
        return self.powerstate
            
        #else:
        #    self.powerstate ='unknown'
        #    logger.error('Could nort processes server state')
    
        

    def power_off(self):
        server = manager.get_device(METAL_SERVER_UUID)
        logger.info('IPMI BMC Power_Off request.')
        logger.info('Metal Server State: %s' % server.state)
        # IPMI will ask to turn a server off but expect a return of "on" till it is "off"
        # Chassis Power Control: Up/Off
        # IPMItool will keep the session open after the first request and request again till Down/Off
        if server.state == 'active':
            try:
                logger.info('Metal API: power OFF %s', METAL_SERVER_UUID)
                server.power_off()
                self.powerstate = 'on'
            except packet.baseapi.ResponseError as e:
                logger.error('Metal API returned %s as error to power OFF request'
                % e)
                self.powerstate = 'unknown'
        elif server.state == 'inactive':
            self.powerstate = 'off'
            logger.debug('Metal server is already off')
        else:
            logger.debug('Metal server will return state unknown, expected')
            self.powerstate = 'unknown'
        
        #return self.powerstate
        #self.powerstate = 'off'

    def power_on(self):
        server = manager.get_device(METAL_SERVER_UUID)
        logger.info('IPMI BMC Power_On request.')
        logger.info('Metal Server State: %s' % server.state)
        # IPMI will ask to turn a server on but expect a return of "off" till it is "on"
        # Chassis Power Control: Down/On 
        if server.state == 'active':
            self.powerstate = 'on'
            logger.debug('Metal server is already on')
        elif server.state == 'inactive':
            try: 
                logger.info('Metal API: power ON %s', METAL_SERVER_UUID)
                server.power_on()
            except packet.baseapi.ResponseError as e:
                logging.error('Metal API returned %s as error to power ON request' % e)
                self.powerstate = 'unknown'
        else:
            self.powerstate = 'unknown'
        self.powerstate

    def power_reset(self):
        logger.info('IPMI BMC Power_Reset request.')
        server = manager.get_device(METAL_SERVER_UUID)
        if server.state == 'inactive':
            server.power_on()
            try:
                logger.debug('Metal Server: is OFF for Power_Reset call, issuing power ON')
                self.powerstate = 'on'
            except packet.baseapi.ResponseError as e:
                logging.error('Metal API returned %s as error to power ON request' % e)
                self.powerstate = 'unknown'
        else:
            logger.debug('Metal API: REBOOT server')
            server.reboot()
        # warm boot
        self.powerstate = 'on'

    def power_cycle(self):
        logger.info('IPMI BMC Power_Cycle request.')
        server = manager.get_device(METAL_SERVER_UUID)
        if server.state == 'inactive':
            server.power_on()
            try:
                logger.debug('Metal Server: is OFF for Power_Cycle call, issuing power ON')
                self.powerstate = 'on'
            except packet.baseapi.ResponseError as e:
                logging.error('Metal API returned %s as error to power ON request' % e)
                self.powerstate = 'unknown'
        else:
            logger.debug('Metal API: REBOOT server')
            server.reboot()
        # cold boot
        self.powerstate = 'off'
        self.powerstate = 'on'

    def power_shutdown(self):
        logger.info('IPMI BMC Power_Shutdown request.')
        self.powerstate = 'off'
