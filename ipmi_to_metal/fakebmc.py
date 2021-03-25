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


        # | FNC:CMD   | NetFunc         | Command                             |
        # | --------- | ----------------|------------------------------------ |
        # | 0x00:0x00 | Chassis         | Chassis Capabilities                |
        # | 0x00:0x01 | Chassis         | Get Chassis Status                  |
        # | 0x00:0x02 | Chassis         | Chassis Control                     |
        # | 0x00:0x08 | Chassis         | Set System Boot Options             |
        # | 0x00:0x09 | Chassis         | Get System Boot Options             |
        # | 0x04:0x2D | Sensor/Event    | Get Sensor Reading                  |
        # | 0x04:0x2F | Sensor/Event    | Get Sensor Type                     |
        # | 0x04:0x30 | Sensor/Event    | Set Sensor Reading and Event Status |
        # | 0x06:0x01 | App             | Get Device ID                       |
        # | 0x06:0x02 | App             | Cold Reset                          |
        # | 0x06:0x03 | App             | Warm Reset                          |
        # | 0x06:0x04 | App             | Get Self Test Results               |
        # | 0x06:0x08 | App             | Get Device GUID                     |
        # | 0x06:0x22 | App             | Reset Watchdog Timer                |
        # | 0x06:0x24 | App             | Set Watchdog Timer                  |
        # | 0x06:0x2E | App             | Set BMC Global Enables              |
        # | 0x06:0x31 | App             | Get Message Flags                   |
        # | 0x06:0x35 | App             | Read Event Message Buffer           |
        # | 0x06:0x36 | App             | Get BT Interface Capabilities       |
        # | 0x06:0x40 | App             | Set Channel Access                  |
        # | 0x06:0x41 | App             | Get Channel Access                  |
        # | 0x06:0x42 | App             | Get Channel Info Command            |
        # | 0x0A:0x10 | Storage         | Get FRU Inventory Area Info         |
        # | 0x0A:0x11 | Storage         | Read FRU Data                       |
        # | 0x0A:0x12 | Storage         | Write FRU Data                      |
        # | 0x0A:0x40 | Storage         | Get SEL Info                        |
        # | 0x0A:0x42 | Storage         | Reserve SEL                         |
        # | 0x0A:0x44 | Storage         | Add SEL Entry                       |
        # | 0x0A:0x48 | Storage         | Get SEL Time                        |
        # | 0x0A:0x49 | Storage         | Set SEL Time                        |
        # | 0x0C:0x01 | Transport       | Set LAN Configuration Parameters    |
        # | 0x0C:0x02 | Transport       | Get LAN Configuration Parameters    |
        # | 0x2C:0x00 | Group Extension | Group Extension Command             |
        # | 0x2C:0x03 | Group Extension | Get Power Limit                     |
        # | 0x2C:0x04 | Group Extension | Set Power Limit                     |
        # | 0x2C:0x05 | Group Extension | Activate/Deactivate Power Limit     |
        # | 0x2C:0x06 | Group Extension | Get Asset Tag                       |
        # | 0x2C:0x08 | Group Extension | Set Asset Tag                       |


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
METAL_SERVER_IPXE_URL = os.getenv("METAL_SERVER_IPXE_URL")
if METAL_AUTH_TOKEN is None:
    logger.error("OS ENV variable METAL_AUTH_TOKEN= must be set")
    sys.exit(1)
elif METAL_SERVER_UUID is None:
    logger.error("OS ENV variable METAL_SERVER_UUID= must be set")
    sys.exit(1)
elif METAL_SERVER_IPXE_URL is None:
    logger.error("OS ENV variable METAL_SERVER_IPXE_URL= must be set")
    sys.exit(1)

manager = packet.Manager(auth_token=METAL_AUTH_TOKEN)


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
        server = manager.get_device(METAL_SERVER_UUID)
        logger.info('IPMI BMC Set_Boot_Device request.')
        logger.info('IPMI BMC bootdevice request is for %s' % bootdevice)
        logger.info('Metal Server PXE state is %s' % server.always_pxe)
        if bootdevice == 'network':
            logger.info('Metal Server iPXE URL being set to: %s' % METAL_SERVER_IPXE_URL)
            logger.info('Metal Server always_ipxe being set to True')
            server.ipxe_script_url = METAL_SERVER_IPXE_URL
            server.always_pxe = True
            server.update()
        if bootdevice == 'hd':
            logger.info('Metal Server always_ipxe being set to False')
            server.always_pxe = False
            server.update()
        self.bootdevice = bootdevice

    def cold_reset(self):
        server = manager.get_device(METAL_SERVER_UUID)
        logger.info('IPMI BMC Cold_Reset request.')
        server.reboot()
        self.powerstate = 'off'
        #self.bootdevice = 'default'

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
                logger.error('Metal API returned %s as error to power OFF request' % e)
                self.powerstate = 'unknown'
        elif server.state == 'inactive':
            self.powerstate = 'off'
            logger.debug('Metal server is already off')
        else:
            logger.debug('Metal server will return state unknown, expected')
            self.powerstate = 'unknown'

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
                logger.error('Metal API returned %s as error to power ON request' % e)
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
                logger.error('Metal API returned %s as error to power ON request' % e)
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
                logger.error('Metal API returned %s as error to power ON request' % e)
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
    
    # This is a horrible horrible thing to do
    # Todo redo all of this
    # https://opendev.org/x/pyghmi/src/branch/master/pyghmi/ipmi/bmc.py#L162
    def custom_handle_raw_request(self, request, session):
        logger.debug('HIT Custom Handler command is %s', hex(request['command']))
        #try:
        if request['netfn'] == 6:
            if request["command"] == 0x42: # 0x06 0x42 
                logger.debug('wut')
                self.session._send_ipmi_net_payload(data=get_channel_info())
            elif request["command"] == 0x41: # 0x06 0x41 (automatic subcall of 0x42)
                logger.debug('WAT')
                self.session._send_ipmi_net_payload(data=get_channel_settings())
        elif request['netfn'] == 10:
            if request["command"] == 0x10: # 0x0a 0x10 (automatic subcall of 0x42)
                logger.debug('wott')
                self.session._send_ipmi_net_payload(data=get_fru_inventory_area_info())
            elif request["command"] == 0x11: # 0x0a 0x11 (automatic subcall of 0x42)
                zeros_number = len([num for num in request.get("data") if num == 0x00])
                logger.error(zeros_number)
                if zeros_number == 3 and 0x08 in request.get("data"):
                    logger.debug('WAT1')
                    self.session._send_ipmi_net_payload(data=read_fru_data1())                
                elif zeros_number == 2 and 0x08 in request.get("data") and 0x02 in request.get("data"):
                    logger.debug('WAT2')
                    self.session._send_ipmi_net_payload(data=read_fru_data2())
                elif zeros_number == 2 and 0x08 in request.get("data") and 0x20 in request.get("data"):
                    logger.debug('WAT3')
                    self.session._send_ipmi_net_payload(data=read_fru_data3())
                elif zeros_number == 2 and 0x08 in request.get("data") and 0x28 in request.get("data"):
                    logger.debug('WAT4')
                    self.session._send_ipmi_net_payload(data=read_fru_data4())
                elif zeros_number == 2 and 0x02 in request.get("data") and 0x30 in request.get("data"):
                    logger.debug('WAT5')
                    self.session._send_ipmi_net_payload(data=read_fru_data5())
                elif zeros_number == 2 and 0x20 in request.get("data") and 0x30 in request.get("data"):
                    logger.debug('WAT6')
                    self.session._send_ipmi_net_payload(data=read_fru_data6())                    
                elif zeros_number == 2 and 0x10 in request.get("data") and 0x50 in request.get("data"):
                    logger.debug('WAT7')
                    self.session._send_ipmi_net_payload(data=read_fru_data7())
                elif zeros_number == 2 and 0x60 in request.get("data") and 0x02 in request.get("data"):
                    logger.debug('WAT8')
                    self.session._send_ipmi_net_payload(data=read_fru_data8())
                elif zeros_number == 2 and 0x60 in request.get("data") and 0x20 in request.get("data"):
                    logger.debug('WAT9')
                    self.session._send_ipmi_net_payload(data=read_fru_data9())
                elif zeros_number == 2 and 0x80 in request.get("data") and 0x20 in request.get("data"):
                    logger.debug('WAT10')
                    self.session._send_ipmi_net_payload(data=read_fru_data10())                              
        # except:
           # logger.error('Shouldnt be here')
        
        
#Taken from 
# https://github.com/kurokobo/virtualbmc-for-vsphere/blob/master/vbmc4vsphere/vbmc.py#L350
def get_channel_info():
    logger.debug('Hit channel data son')
    channel_data = [
        0x02,  # channel number = 2
        0x04,  # channel medium type = 802.3 LAN
        0x01,  # channel protocol type = IPMB-1.0
        0x80,  # session support = multi-session
        0xF2,  # vendor id = 7154
        0x1B,  # vendor id = 7154
        0x00,  # vendor id = 7154
        0x00,  # reserved
        0x00,  # reserved
    ]
    return channel_data
    
#Taken from 
# https://github.com/kurokobo/virtualbmc-for-vsphere/blob/master/vbmc4vsphere/vbmc.py#L350
def get_channel_settings():
    logger.debug('Hit channel settings CHILD')
    channel_settings = [
        0x12,
        0x04, 
    ]
    return channel_settings
    
def get_fru_inventory_area_info():
    logger.debug('Hit get_fru_inventory_area_info')
    fru_area_info = [
        0x00,
        0x01,
        0x00,
        # 0x20,
        # 0x31,
        # 0x32,
        # 0x54,
        # 0x52,
        # 0x46,
        # 0xc4,
        # 0x4e,
        # 0x4f,
        # 0x4e,
        # 0x45,
        # 0xcf,
        # 0x53,
        # 0x32,
        # 0x31,
        # 0x31,
        # 0x36,
        # 0x37,
        # 0x38,
        # 0x58,
        # 0x39,
        # 0x32,
        # 0x32,
        # 0x36,
        # 0x34,
        # 0x38,
        # 0x37,
        # 0xc0,
        # 0xc0,
        # 0xc1,
        # 0x00,
        # 0x00,
        # 0x80,
    ]
    return fru_area_info

def read_fru_data1():
    logger.debug('Hit read_fru_data1')
    fru_data1 = [
        0x08,
        0x01,
        0x00,
        0x01,
        0x06,
        0x0c,
        0x00,
        0x00,
        0xec,
    ]
    return fru_data1

def read_fru_data2():
    logger.debug('Hit read_fru_data2')
    fru_data2 = [
        0x02,
        0x01,
        0x05,
    ]
    return fru_data2
    
def read_fru_data3():
    logger.debug('Hit read_fru_data3')
    fru_data3 = [
        0x20,
        0x01,
        0x05,
        0x01,
        0xd1,
        0x43,
        0x53,
        0x45,
        0x2d,
        0x39,
        0x33,
        0x39,
        0x48,
        0x53,
        0x2d,
        0x52,
        0x32,
        0x4b,
        0x30,
        0x34,
        0x42,
        0x50,
        0xcf,
        0x43,
        0x39,
        0x33,
        0x39,
        0x30,
        0x41,
        0x48,
        0x31,
        0x37,
        0x41,
    ]
    return fru_data3

def read_fru_data4():
    logger.debug('Hit read_fru_data4')
    fru_data4 = [
        0x08,
        0x34,
        0x30,
        0x30,
        0x31,
        0x37,
        0xc1,
        0x00,
        0x18,

    ]
    return fru_data4

def read_fru_data5():
    logger.debug('Hit read_fru_data5')
    fru_data5 = [
        0x02,
        0x01,
        0x06,
    ]
    return fru_data5
    
def read_fru_data6():
    logger.debug('Hit read_fru_data6')
    fru_data6 = [
        0x20,
        0x01,
        0x06,
        0x00,
        0x80,
        0x3e,
        0xb9,
        0xca,
        0x53,
        0x75,
        0x70,
        0x65,
        0x72,
        0x6d,
        0x69,
        0x63,
        0x72,
        0x6f,
        0xc4,
        0x4e,
        0x4f,
        0x4e,
        0x45,
        0xcc,
        0x5a,
        0x4d,
        0x31,
        0x39,
        0x31,
        0x53,
        0x30,
        0x32,
        0x38,
    ]
    return fru_data6
    
def read_fru_data7():
    logger.debug('Hit read_fru_data7')
    fru_data7 = [
        0x10,
        0x32,
        0x36,
        0x35,
        0xc8,
        0x58,
        0x31,
        0x31,
        0x53,
        0x53,
        0x45,
        0x2d,
        0x46,
        0xc0,
        0xc1,
        0x00,
        0xa2,
    ]
    return fru_data7

def read_fru_data8():
    logger.debug('Hit read_fru_data8')
    fru_data8 = [
        0x02,
        0x01,
        0x08,
    ]
    return fru_data8
    
def read_fru_data9():
    logger.debug('Hit read_fru_data9')
    fru_data9 = [
        0x20,
        0x01,
        0x08,
        0x00,
        0xca,
        0x53,
        0x75,
        0x70,
        0x65,
        0x72,
        0x6d,
        0x69,
        0x63,
        0x72,
        0x6f,
        0xc4,
        0x4e,
        0x4f,
        0x4e,
        0x45,
        0xd1,
        0x53,
        0x50,
        0x53,
        0x2d,
        0x35,
        0x30,
        0x33,
        0x39,
        0x4d,
        0x53,
        0x2d,
        0x48,
    ]
    return fru_data9
    
def read_fru_data10():
    logger.debug('Hit read_fru_data10')
    fru_data10 = [
        0x20,
        0x31,
        0x32,
        0x54,
        0x52,
        0x46,
        0xc4,
        0x4e,
        0x4f,
        0x4e,
        0x45,
        0xcf,
        0x53,
        0x32,
        0x31,
        0x31,
        0x36,
        0x37,
        0x38,
        0x58,
        0x39,
        0x32,
        0x32,
        0x36,
        0x34,
        0x38,
        0x37,
        0xc0,
        0xc0,
        0xc1,
        0x00,
        0x00,
        0x80,
    ]
    return fru_data10