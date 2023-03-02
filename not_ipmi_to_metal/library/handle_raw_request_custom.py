# import pyghmi.ipmi.bmc as bmc
import traceback

import logging
import sys

logger = logging.getLogger("not_ipmi_to_metal")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


def handle_raw_request_patch(self, request, session):
    try:
        if request["netfn"] == 6:
            if request["command"] == 1:  # get device id
                return self.send_device_id(session)
            elif request["command"] == 2:  # cold reset
                return session.send_ipmi_response(code=self.cold_reset())
            elif request["command"] == 0x37:  # get system guid
                return self.get_system_guid(session)
            elif request["command"] == 0x48:  # activate payload
                return self.activate_payload(request, session)
            elif request["command"] == 0x49:  # deactivate payload
                return self.deactivate_payload(request, session)
        elif request["netfn"] == 0:
            if request["command"] == 1:  # get chassis status
                return self.get_chassis_status(session)
            elif request["command"] == 2:  # chassis control
                return self.control_chassis(request, session)
            elif request["command"] == 8:  # set boot options
                return self.set_system_boot_options(request, session)
            elif request["command"] == 9:  # get boot options
                return self.get_system_boot_options(request, session)
        elif request["netfn"] == 10:  # FRU handling
            if request["command"] == 0x10:
                return self.get_fru_inventory_area_info(session)
            elif request["command"] == 0x11:
                zeros_number = len([num for num in request.get("data") if num == 0x00])
                if zeros_number == 3 and 0x08 in request.get("data"):
                    logger.info("IPMI fru print 0 called likely")
                    return self.get_fru_0_0(session)
                elif (
                    zeros_number == 2
                    and 0x08 in request.get("data")
                    and 0x02 in request.get("data")
                ):
                    return self.get_fru_0_1(session)
                # elif zeros_number == 2 and 0x08 in request.get("data") and 0x18 in request.get("data"):
                elif (
                    zeros_number == 2
                    and 0x08 in request.get("data")
                    and 0x20 in request.get("data")
                ):
                    return self.get_fru_0_2(session)
                elif (
                    zeros_number == 2
                    and 0x28 in request.get("data")
                    and 0x20 in request.get("data")
                ):
                    return self.get_fru_0_3(session)

        else:
            session.send_ipmi_response(code=0xC1)
    except NotImplementedError:
        session.send_ipmi_response(code=0xC1)
    except Exception:
        session._send_ipmi_net_payload(code=0xFF)
        traceback.print_exc()
