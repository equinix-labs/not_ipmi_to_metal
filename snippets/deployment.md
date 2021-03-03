### not_ipmi_to_metal deployment guide



This doc is intended to provide a deployment guide for the not_ipmi_to_metal service. It is presumed that there are other ways to deploy this, this doc is only presenting a path that is intended to be tested as *reasonably* viable given the wild west nature of the project and code.


1) Launch an Equinix Metal instance, which will be our host for the `ipmi_to_metal` services
    * Instance can be as small as is allowed in the account, a `c3.small.x86` would be more then capable
    * Instance should provisioned with `Ubuntu 20.04 LTS` as the chosen OS
    * Optionally, leverage the `#cloud-config` available [boilerplate here](https://github.com/dlotterman/metal_code_snippets/blob/main/boiler_plate_cloud_inits/ubuntu2004.yaml)
    * This host will act as our host for the ipmi_to_metal service
    * All other options can be left at defaults, including Public IP connectivity, which will be needed.

2) Prep host software
    * Note that the instance may still be following up from tasks from the supplied `#cloud-config` data
        * For example, a lock may still be in place on package updates as `apt-get` finishes up from the `#cloud-config` 
    * Install Docker according to preferred best practices, [example here from Docker Docs](https://docs.docker.com/engine/install/ubuntu/)

3) Prepare an ElasticIP to host the endpoint
    * Provision a private [ElasticIP](https://metal.equinix.com/developers/docs/networking/elastic-ips/)
        * This can also be done by loading a server's page in the console and selecting **Networks** -> **"Assign New Elastic"** blue bottom -> **Selecting "Private IPv4" -> Selecting a block of assigned private IPs** -> Select **/32** as the length -> Picking an individual /32 -> Clicking **"Add"**
    * With the ElasticIP provisioned in the Metal platform, the IP can be attached to the bond of the service host. 
        * For example for the private ElasticIP `10.99.120.142/32`
            * `ip addr add 10.99.120.142 dev bond0`
            * Note this example is not persistant accross reboots by design, to persist, follow a documented path for persistent configuration of IPs
    * This ElasticIP will functionally become a Metal Servers IPMI endpoint, where normally when specifying an IP address attached to the lifecycle controller of a box (For example iDRAC), this ElasticIP will now be specified and will be specifically attached as the IP for the IPMI endpoint for a specific Metal instance

4) Begin service building and turnup on host
    * Pull down this repo: `git clone https://github.com/dlotterman/not_ipmi_to_metal.git`
    * `cd` into the directory `cd not_ipmi_to_metal/`
    * Build the Docker image locally with:
      * `docker -v build  -t ipmi_to_metal:latest .`
    * Start the Docker container with:
        ```
        export METAL_AUTH_TOKEN=$(YOUR_RW_METAL_TOKEN_HERE) && \
        export METAL_SERVER_UUID=$(YOUR_METAL_INSTANCE_UUID_HERE) && \
        docker run -d --name ipmi_to_metal_$SERVER_HUMAN_NAME \
        -e METAL_AUTH_TOKEN \
        -e METAL_SERVER_UUID \
        -p $(ELASTIC_IP_HERE):623:623/udp \
        ipmi_to_metal:latest
        ```
        
        * Where `METAL_AUTH_TOKEN` is a API Token for Metal with R/W access to the Metal instance
        * And `METAL_SERVER_UUID` is the UUID of an instance that can be gleaned from the API or the servers description page, example: `https://console.equinix.com/devices/3c527c68-cf7f-REMIANINGUUID_STRING_HERE/network`
        * And `SERVER_HUMAN_NAME` is a human readable string that will help identify the running Docker container as a service for a specific Metal instance. For example if this instance of `ipmi_to_metal` we're supporting a Metal instance called `api01`, the full string here could read `ipmi_to_metal_api01`
        * And the ElasticIP is the IP we provisioned and assigned above
    * If the container turned up succesfully, we can see the following in the containers log:
        ```
        # docker logs ipmi_to_metal_power-trash
        2021-03-03 20:30:36,299 : INFO : fakebmc : IPMI BMC initialized.
        2021-03-03 20:30:36,299 : INFO : ipmisim : CloudStack IPMI Sim BMC initialized
        2021-03-03 20:30:36,300 : INFO : ipmi_to_metal : Started ipmi_to_metal server on 0.0.0.0:623
        ```
        
5) Test the endpoint
    * From another host on in the same project, test IPMI access to the endpoint / ElasticIP
    ```
    # ipmitool -I lanplus -H 10.99.120.142 -U admin -P password chassis power status
    Chassis Power is off
    ```
    * Issuing an IPMI power change request should be visible in the Metal interface as well as the Docker logs of the container
    ```
    # ipmitool -I lanplus -H 10.99.120.142 -U admin -P password chassis power on
    Chassis Power Control: Up/On
    ```
    ```
    # docker logs ipmi_to_metal_power-trash
    2021-03-03 20:34:40,421 : DEBUG : ipmisim : Incoming IPMI traffic from ('10.99.120.137', 48270)
    2021-03-03 20:34:40,557 : INFO : fakebmc : IPMI BMC Power_On request.
    2021-03-03 20:34:40,557 : INFO : fakebmc : Metal Server State: inactive
    2021-03-03 20:34:40,557 : INFO : fakebmc : Metal API: power ON 26bd2e64-SCRUBBED
    2021-03-03 20:34:40,710 : DEBUG : fakesession : IPMI response sent to ('10.99.120.137', 48270)
    2021-03-03 20:34:40,712 : DEBUG : ipmisim : Incoming IPMI traffic from ('10.99.120.137', 48270)
    2021-03-03 20:34:40,712 : DEBUG : fakesession : IPMI response sent to ('10.99.120.137', 48270)
    2021-03-03 20:34:40,713 : DEBUG : ipmisim : IPMI response sent (Close Session) to ('10.99.120.137', 48270)
    2021-03-03 20:34:40,713 : DEBUG : ipmisim : IPMI Session closed 10.99.120.137
    ```
   
6) Congratulations, you now have a dedicated IPMI endpoint for your Metal instance!
