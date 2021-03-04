# not_ipmi_to_metal

`not_ipmi_to_metal` is a fake IPMI server / endpoint that takes the hard work and logic from [shapeblue/ipmisim](https://github.com/shapeblue/ipmisim) and wraps+extends it in a way as to function as a "inbound IPMI request to Metal API / SSH / openipmi / other" proxy.

To be explicit, the code quality of this repo should be considered *hackathon* grade. This repo is purely for exploratory and collaborative purposes.

[Quick Deployment Guide](https://github.com/dlotterman/not_ipmi_to_metal/blob/main/snippets/deployment.md)

[Development Intent](https://github.com/dlotterman/not_ipmi_to_metal/blob/main/snippets/development.md)

[Equinix Metal](https://metal.equinix.com/), as an Infrastructure as a Service cloud, provides single-tenant, Bare Metal Servers as on-demand, cloudy provisioned compute & storage instances. In the world of "Bare Metal", [IPMI](https://en.wikipedia.org/wiki/Intelligent_Platform_Management_Interface) is often used as a control-plane protocol and actor for [managing](https://www.thomas-krenn.com/en/wiki/Setup_the_IPMI_remote_management_interface) the physical characteristics of a chassis; power on, power off, reboot, sensor data etc. Those IPMI actions are normally targetted at the "lifecycle controller" of a server chassis, for example with a Dell chassis this would be the [iDRAC](https://en.wikipedia.org/wiki/Dell_DRAC) card, for HPE it's [iLO](https://en.wikipedia.org/wiki/HP_Integrated_Lights-Out), and for SuperMicro it's confusingly enough [IPMI](https://www.supermicro.com/en/solutions/management-software/ipmi-utilities). 

By nature of being a Bare Metal cloud, Equinix Metal isolates and removes network access to this lifecycle controller for a variety of reasons, including it's own automation needs as well as security and operational concerns. Instead of providing raw IPMI acess, Metal exposes an [HTTP API](https://metal.equinix.com/developers/api/) which provides analogous [functionality](https://metal.equinix.com/developers/api/devices/#devices-performAction), which is more than sufficient for most kinds of Metal deployments. 

This is problematic for software stacks dependant on having netwok enabled IPMI access to the lifecycle controller. Software stacks such as OpenStack with it's Ironic package expect direct IPMI access to a chassis lifecycle controller, as management of underlying physical hardware is a core concern of that architecure.

`not_ipmi_to_metal` will act as an exploratory shim, allowing IPMI requests that would normally be directed at a Bare Metal instance's lifecycle controller to instead be mimicked against a variety of endpoints in order to best match feature functionality, including the Metal API itself. The intent is to provide

1) A potential way of loosening the tight coupling on IPMI access dependant on some stacks for the purposes of evaluating Equinix Metal. 
    * For orginzations looking to potentially deploy workloads onto Equinix Metal, it can often be burdensome to evaluate the platform without de-coupling the requirement for IPMI access. Leveraging this as a non-production shim, it should be possible to evaluate what a non-IPMI coupled deployment would look like.

2) Learn more about the operational realities of deploying *this kind of thing* and the potential requirements of a more permanent, supportable `ipmi_to_metal`
