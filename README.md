# not_ipmi_to_metal

`not_ipmi_to_metal` is an emulated IPMI server / endpoint that receives native IPMIv2.0 lanplus formatted requests and proxies the intended action against the Equinix Metal API, functionally allowing for the control of an Equinix Metal instance via tools like `ipmitool`.

[![Equinix Metal Website](https://img.shields.io/badge/Website%3A-metal.equinix.com-blue)
[![Actively Maintained](https://img.shields.io/badge/Maintenance%20Level-Actively%20Maintained-green.svg)](https://gist.github.com/cheerfulstoic/d107229326a01ff0f333a1d3476e068d)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

The intent is to provide a de-coupling between software stacks that are IPMI control dependant, allowing those software stacks to control Equinix Metal instance's without software re-writes.

It is not intended to be a fully featured IPMI endpoint/ BMC / Lifecycle Controller, and is singularly focused on `chassis bootdev` and `chassis power` contexts.

```
$ python not_ipmi_to_metal/not_ipmi_to_metal.py --help
usage: not_ipmi_to_metal [-h] [--port PORT] [--user IPMIUSER] [--password IPMIPASS] [--metaltoken METALTOKEN]
                         [--metaluuid METALUUID]

Pretend to be a Metal instances BMC and proxy IPMI commands to the Metal API. Note some variables can be set by ENV

optional arguments:
  -h, --help            show this help message and exit
  --port PORT           (UDP) port to listen on (default: 623)
  --user IPMIUSER       IPMI username to expect (default: admin)
  --password IPMIPASS   IPMI password to expect (default: password)
  --metaltoken METALTOKEN
                        Equinix Metal Read / Write API Token, will get from ENV METAL_AUTH_TOKEN if unset (default:
                        None)
  --metaluuid METALUUID
                        UUID of the Equinix Metal instance, will get from METAL_INSTANCE_UUID if unset (default: None)
```


```
2022-04-15 18:04:50,204 - not_ipmi_to_metal - INFO - not_metal_to_ipmi service for instance UUID: 87b9b0ac-dd7e-4a9d-b156-6736d57d6364 starting on port 623
2022-04-15 18:05:01,065 - not_ipmi_to_metal - INFO - IPMI BMC Power_On request.
2022-04-15 18:05:02,297 - not_ipmi_to_metal - INFO - IPMI BMC Power_On request.
2022-04-15 18:05:24,771 - not_ipmi_to_metal - INFO - IPMI BMC Power_Off request.
```

## Credits and references

* The [first incarnation of this utility](https://github.com/dlotterman/not_ipmi_to_metal/tree/4c9193f3319e3af798ff03e717672a463209ff4a) lifted heavily from [shapeblue/ipmisim](https://github.com/shapeblue/ipmisim/tree/main/ipmisim)
* The current incarnation of this utility lifts heavily from [open/stack/virtualvbmc](https://github.com/openstack/virtualbmc)
* The real heavy lifting of this utility comes from the [pyghmi](https://opendev.org/x/pyghmi) project
* This utility levarages the [Equinix Metal Python Library](https://opendev.org/x/pyghmi)
* The Equinix Metal API is [well documented here](https://metal.equinix.com/developers/api/)

## Installation

`not_ipmi_to_metal` is intended to be deployed as a application container, and should be deployeable via `docker`, `podman` or `containerd`

`not_ipmi_to_metal` is available as a hosted container via Docker Hub

[More detailed installation steps detailed here](docs/install.md)

## Getting help and support

`not_ipmi_to_metal` is entirely self-supported from an end operator perspective, and no active support is provided. Please feel free to reach out to the repository owner with questions, concerns or requests.

To be explicit, this project is not affiliated with Equinix Metal and is not supported by Equinix Metal in any way.


## Versioning

Versioning is elementary. Current version is maintained in the `version` [file at the root of this repository](version), where Docker tags will reference that version.

## Diagram

![](https://s3.us-east-1.wasabisys.com/metalstaticassets/not_ipmi_to_metal_openstack.JPG)

## TODO

* Equinix Metal `packet-python` usage should be classed or libbed
    * More pythonic
    * try / except to better handle API failures in context
* Expose a more elegant [custom handler like we had here](https://github.com/dlotterman/not_ipmi_to_metal/blob/12f44ce81337ee47e7c197db95d51fb30f4d194f/ipmi_to_metal/fakebmc.py#L253)

