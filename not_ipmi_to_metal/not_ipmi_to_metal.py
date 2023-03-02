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

# This is a simple, but working proof of concept of using pyghmi.ipmi.bmc to
# control a Metal instance, it is lifted almost entirely from OpenStack's VBMC
# https://github.com/openstack/virtualbmc
# Thank you to that group for all the effort

import argparse
import sys
import packet
import logging
import os
import uuid
import re

import pyghmi.ipmi.bmc as bmc
import library.handle_raw_request_custom

logger = logging.getLogger('not_ipmi_to_metal')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class metalbmc(bmc.Bmc):

    def __init__(self, authdata, port, metaltoken, metaluuid):
        super(metalbmc, self).__init__(authdata, port)
        metalbmc.handle_raw_request = library.handle_raw_request_custom.handle_raw_request_patch
        logger.info(
            'not_metal_to_ipmi service for instance UUID: %s starting on port %s', metaluuid, port)
        self.state = 'on'
        self.stream = None
        self.run_console = False
        self.sol_thread = None
        self.metaltoken = metaltoken
        self.metaluuid = metaluuid

        self.metal_manager = packet.Manager(auth_token=self.metaltoken)

    def get_boot_device(self):
        logger.info('IPMI BMC Get_Boot_Device request.')
        return self.bootdevice

    def set_boot_device(self, bootdevice):
        metal_instance = self.metal_manager.get_device(self.metaluuid)
        logger.info('IPMI BMC Set_Boot_Device request.')
        if bootdevice == 'network':
            logger.info('Metal Server always_ipxe being set to True')
            metal_instance.always_pxe = True
            metal_instance.update()
        if bootdevice == 'hd':
            logger.info('Metal Server always_ipxe being set to False')
            metal_instance.always_pxe = False
            metal_instance.update()
        self.bootdevice = bootdevice
        return

    def cold_reset(self):
        logger.info('IPMI BMC Power_Reset request.')
        metal_instance = self.metal_manager.get_device(self.metaluuid)
        if metal_instance.state == 'inactive':
            metal_instance.power_on()
            self.powerstate = 'on'
        else:
            metal_instance.reboot()
        self.powerstate = 'on'

    def get_power_state(self):
        logger.info('IPMI BMC Get_Power_State request.')
        metal_instance = self.metal_manager.get_device(self.metaluuid)
        if metal_instance.state == 'active':
            self.powerstate = 'on'
        if metal_instance.state == 'powering_on':
            self.powerstate = 'on'
        if metal_instance.state == 'powering_off':
            self.poweroff = 'off'
        elif metal_instance.state == 'inactive':
            self.powerstate = 'off'
        return self.powerstate

    def power_off(self):
        logger.info('IPMI BMC Power_Off request.')
        metal_instance = self.metal_manager.get_device(self.metaluuid)
        if metal_instance.state == 'active':
            try:
                metal_instance.power_off()
            except:
                logging.critical(
                    'IPMI BMC could not poweroff instance via Metal API')
                self.powerstate = 'unknown'
        self.powerstate = 'off'

        self.powerstate

    def power_on(self):
        logger.info('IPMI BMC Power_On request.')
        metal_instance = self.metal_manager.get_device(self.metaluuid)
        if metal_instance.state == 'active':
            self.powerstate = 'on'
        if metal_instance.state == 'inactive':
            try:
                metal_instance.power_on()
                self.powerstate = 'on'
            except:
                logging.critical(
                    'IPMI BMC could not powerob instance via Metal API')
                self.powerstate = 'unknown'
        self.powerstate

    def power_reset(self):
        logger.info('IPMI BMC Power_Reset request.')
        metal_instance = self.metal_manager.get_device(self.metaluuid)
        if metal_instance.state == 'inactive':
            metal_instance.power_on()
            self.powerstate = 'on'
        else:
            metal_instance.reboot()
        self.powerstate = 'on'

    def power_cycle(self):
        logger.info('IPMI BMC Power_Cycle request.')
        metal_instance = self.metal_manager.get_device(self.metaluuid)
        if metal_instance.state == 'inactive':
            metal_instance.power_on()
            self.powerstate = 'on'
        else:
            metal_instance.reboot()
        self.powerstate = 'on'

    def power_shutdown(self):
        logger.info('IPMI BMC Power_Shutdown request.')
        metal_instance = self.metal_manager.get_device(self.metaluuid)
        if metal_instance.state == 'active':
            try:
                metal_instance.power_off()
            except:
                logging.critical(
                    'IPMI BMC could not poweroff instance via Metal API')
                self.powerstate = 'unknown'
        self.powerstate = 'off'
        self.powerstate

    #This is extremely broken. UUID version mismatches, very difficult
    def get_system_guid(self, session):
        response_data = []
        for char in re.findall('..', uuid.UUID(self.metaluuid).hex):
            portion_to_hex = str.format('0x{0}', char)
            response_data.append(int(portion_to_hex, 16))
        session.send_ipmi_response(code=0x00, data=response_data)

    def get_fru_inventory_area_info(self, session):    
        logger.debug('get_fru_inventory_area_info requested')
        fru_area_info = [
            0x00,
            0x08,
            0x00,

        ]
        session.send_ipmi_response(code=0x00, data=fru_area_info)

### Board Mfg Date        : Sun Dec 31 16:00:00 1995
### Board Part Number     : t3-small-x86-01
    def get_fru_0_0(self, session):    
        logger.debug('get_fru_0 requested')
        fru_data_0_0 = [
            0x08,
            0x01,
            0x00,
            0x00,
            0x01,
            0x00,
            0x00,
            0x00,
            0xfe,
        ]
        session.send_ipmi_response(data=fru_data_0_0)

    def get_fru_0_1(self, session):
        fru_data_0_1 = [
            0x02,
            0x01,
            0x08,
        ]
        session.send_ipmi_response(data=fru_data_0_1)

    def get_fru_0_2(self, session):
        ## Where this goes all 0x00 we could insert an arbitrary string
        fru_data_0_2 = [
            0x20,
            0x01,
            0x08,
            0x19,
            0x00,
            0x00,
            0x00,
            0xd8,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0xc0,
        ]
        session.send_ipmi_response(data=fru_data_0_2)

    def get_fru_0_3(self, session):
        metal_instance = self.metal_manager.get_device(self.metaluuid)
        clean_hostname = metal_instance.hostname
        fru_data_0_3 = [
            0x20,
            0xc0,
            0xd9,
        ]
        for char in clean_hostname:
            fru_data_0_3.append(int(char.encode('utf-8').hex(), 16))
        while len(fru_data_0_3) < 33:
         ####   TODO, this is truly no bueno
         ####   Were just padding the length of the response to the IPMI character break
            fru_data_0_3.append(0x00)
        fru_data_0_3.append(0x7f)
        session.send_ipmi_response(data=fru_data_0_3)


def main():
    parser = argparse.ArgumentParser(
        prog='not_ipmi_to_metal',
        description='Pretend to be a Metal instances BMC and proxy IPMI commands to the Metal API. Note some variables can be set by ENV',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--port',
                        dest='port',
                        type=int,
                        default=623,
                        help='(UDP) port to listen on')
    parser.add_argument('--user',
                        dest='ipmiuser',
                        type=str,
                        default='admin',
                        help='IPMI username to expect')
    parser.add_argument('--password',
                        dest='ipmipass',
                        type=str,
                        default='password',
                        help='IPMI password to expect')
    parser.add_argument('--metaltoken',
                        dest='metaltoken',
                        type=str,
                        default=os.environ.get('METAL_AUTH_TOKEN'),
                        help='Equinix Metal Read / Write API Token, will get from ENV METAL_AUTH_TOKEN if unset')
    parser.add_argument('--metaluuid',
                        dest='metaluuid',
                        type=str,
                        default=os.environ.get('METAL_INSTANCE_UUID'),
                        help='UUID of the Equinix Metal instance, will get from METAL_INSTANCE_UUID if unset')
    args = parser.parse_args()
    if not args.metaltoken or not args.metaluuid:
        exit(parser.print_usage())
    user = args.ipmiuser
    password = args.ipmipass
    mybmc = metalbmc({user: password},
                     port=args.port,
                     metaltoken=args.metaltoken,
                     metaluuid=args.metaluuid)
    mybmc.listen()


if __name__ == '__main__':
    #bmc.handle_raw_request = library.handle_raw_request_custom.handle_raw_request_patch
    library.handle_raw_request_custom.hahatestfunc1()
    sys.exit(main())
