`not_ipmi_to_metal` is intended to be a brush clearing, investigative project to discover and tackle domain speific implementation concerns as are discovered, in anticipation of a more formal, more polished `ipmi_to_metal` project pursuit down the road. The code and glue in this repo is wild wild west by design, as it will likely have to be re-written or re-packaged several times in the pursuit of a better implementation as it's is pursued with more applied test deployments.


Currently, the relevant logic is predominantly in [fakebmc.py](ipmi_to_metal/fakebmc.py), where we can suprisingly quite easily, shove our own logic into the middle of [ipmisim's](https://github.com/shapeblue/ipmisim) BMC / Session handling. This allows us to quickly and easily mock different actions.

### Short-term Todos

* Add `fakebmc.py` shim to support updating a Metal instance's configuration in the platform between iPXE always configurations with a defined iPXE URL specified as  OSENV. This will allow an IPMI call to mimic setting a device to PXE boot and handing off control of the instance to an install chain
* Make IPMI credentials OSENV based


### Target endpoints / abstractions

Currently, `not_ipmi_to_metal` is only leveraging the Equinix Metal API as it's sole endpoint (via `packet-python`) and only for power controls. This is useful for proving out the viability of `ipmi_to_metal`, but in reality there are likely three different endpoints `ipmi_to_metal` could fan out an originating IPMI request to:

1) **Metal API**
    * As we see here, the Metal API can provide the absolute power control IPMI normally reserves for hard reset, and power on / power off actions
 
2) **Host-SSH**
    * While the Metal API can hard reset a Metal instance, it may be preferred to mimic a "soft" reboot call via SSH'ing to the host directly to initiate a soft reboot request. Other examples may be a sensor call, or more complicated call then a simple power state request, where it may be more operationally graceful to SSH into the host to gather data or perform an action than it would be to call a Metal API, or potentially the information we need is simply not present in the API or the Metal platform. 
    * This is probably the most bang for the buck after initial Metal API integration
    * Relatively easy line-of-site with [Paramiko](http://www.paramiko.org/)

3) **Host managed openipmi / freeipmi endpoint**
    * It is conceiveable possible that it would be preferred to strictly mimic an incoming IPMI request with another IPMI request. In this case, we can run an instance of openipmi / freeipmi on the target host directly, and then proxy the incoming IPMI request with a mimic'ed request sent to the host level openipmi endpoint. This would ensure we can conform to IPMI-land strange-isms. 
    * This is the only way I can imagine certain functions like console redirection or remote IPMI shell as a client functiontionality working, though that is likely the highest hanging fruit. 
    * This can be more easily mocked by using the above **Host-SSH** option to call `ipmitool` against the remote host locally to itself. That would keep us from having to build an opinion about deploying a openipmi server / daemon at the host level.


To make this more concrete, consider the following three IPMI requests and how they could be fan'ed out:

* An IPMI request to soft reboot a Metal instance:
  * This request could be sent to the Host OS via SSH, issuing a safe and sane reboot
* An IPMI request to view a TTY / SOL / OOB console  of a Metal instance:
  * Could be fan'ed out to a openipmi daemon runnig on the Metal instance
* An IPMI request to hard power off a Metal instance
  * Could call the Metal API directly to forcefully poweroff the host regadless of other state

### Security
  * By design, `ipmi_to_metal` would insert itself in a high risk management domain, with priviledged credentials and sensitive operations. `not_ipmi_to_metal` should be a security aware project from the beginning as it develops.

### Opinionated Deployment
  * `not_ipmi_to_metal` is currently operationally laborious and extemely fragile. As a better understanding of how it would deployed is reached, it could become significantly more intelligent about autoconfiguration, potentially pursuing tags or another means of gleaning data for self configuration. 

### Other Projects

The OpenStack project has it's ["Virtual BMC"](https://github.com/openstack/virtualbmc) project which can also be poked and proded for inspiration. 

