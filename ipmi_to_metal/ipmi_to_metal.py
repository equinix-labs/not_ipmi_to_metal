import os
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


if  __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ipmi commands to Metal API shim",
                                    prog="ipmi_to_metal")
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
    
