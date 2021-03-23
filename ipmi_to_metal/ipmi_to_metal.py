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

# not_ipmi_to_metal - Fake IPMI endpoint
# forked from ipmisim, which was forked from Conpot
# ipmisim Maintainer - Rohit Yadav <bhaisaab@apache.org>
# C Author: Peter Sooky <xsooky00@stud.fit.vubtr.cz>
# Brno University of Technology, Faculty of Information Technology

import argparse
import logging

import ipmisim


def main(listenip, listenport):

    ipmi_server_context = ipmisim.IpmiServerContext()

    try:
        ipmisim.ThreadedIpmiServer.allow_reuse_address = True
        server = ipmisim.ThreadedIpmiServer((listenip, listenport), ipmisim.IpmiServer)
        logger.info("Started ipmi_to_metal server on %s:" + str(listenport), listenip)
        server.serve_forever()
    except Exception as e:
        logger.error('Could not start ipmi_to_metal server, error %s', e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ipmi commands to Metal API shim", prog="ipmi_to_metal")
    parser.add_argument("--listenip", type=str, help="local IP address for ipmi endpoint to listen on", default="0.0.0.0")
    parser.add_argument("--listenport", type=int, help="port for IPMI server to listen on, default 623 (priviledged)", default=623)

    args = parser.parse_args()

    logger = logging.getLogger('ipmi_to_metal')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    main(args.listenip, args.listenport)
