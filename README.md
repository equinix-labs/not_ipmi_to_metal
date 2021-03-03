# not_ipmi_to_metal

`not_ipmi_to_metal` is a fake IPMI server / ednpoint that takes the hard work and logic from [shapeblue/ipmisim](https://github.com/shapeblue/ipmisim) and wraps+extends it in a way as to function as a "inbound IPMI request to Metal API / SSH / openipmi / other" proxy.

Equinix Metal, as an Infrastructure as a Service cloud, provides single-tenant, Bare Metal Servers as on-demand, cloudy provisioned compute & storage instances. In the world of "Bare Metal", IPMI is often used as a control-plane protocol and actor for controlling the physical characteristics of a chassis; power on, power off, reboot, sensor data etc. Those IPMI actions are normally targetted at the "lifecycle controller" of a server chassis, for example with a Dell chassis this would be the `iDRAC` card, for HPE it's `iLO`, and for SuperMicro it's confusingly enough `IPMI`. 

By nature of being a Bare Metal cloud, Equinix Metal isolates and removes network access to this lifecycle controller for a variety of reasons, including it's own automation needs as well as security and operational concerns. Instead of providing raw IPMI acess, Metal exposes an HTTP API which provides analogous functionality, which is more than sufficient for most kinds of Metal deployments. However this is problematic for software stacks dependant on having IPMI access to the lifecycle controller. Software stacks such as OpenStack for example with it's Ironic package for example, expect IPMI direct access to a chassis lifecycle controller, as management of underlying physical hardware is a core concern of that stack.

`not_ipmi_to_metal` will act as an exploratory shim, allowing IPMI requests that would normally be directed at a Bare Metal instance's lifecycle controler to instead be mimicked against a variety of endpoints in order to best match feature functionality, including the Metal API itself. The intent is to provide

1) A potential way of loosening the tight coupling on IPMI access dependant on some stacks for the purposes of evaluating Equinix Metal. 
    * For orginzations looking to potentially deploy workloads onto Equinix Metal, it can often be burdensome to evaluate the platform without de-coupling the requirement for IPMI access. Leveraging this as a non-production shim, it should be possible to evaluate what a non-IPMI coupled deployment would look like.

2) Learn more about the operational realities of deploying *this kind of thing* and the potential requirements of a more permanent, supportable `ipmi_to_metal`
