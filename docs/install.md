## not_ipmi_to_metal installation

`not_ipmi_to_metal` is hosted as a pre-built container on [Docker Hub](https://hub.docker.com/r/dlotterman/not_ipmi_to_metal)

It can also be built locally with the correct container toolchain locally by checking out this repo.

It is expected that the container toolchain of choice (docker, podman etc) is already installed and correctly configured for container deployments.

* [Docker Install Documentation](https://docs.docker.com/engine/install/ubuntu/)
* [Podman Install Documentation] (https://podman.io/getting-started/installation)

## no-code podman host

[This `cloud-init` file can be used to launch](https://github.com/dlotterman/metal_code_snippets/tree/main/virtual_appliance_host/no_code_with_guardrails) an Equinix Metal Alma instance that will:
* Secure itself with patching and basic operational security steps
* Install [cockpit](https://cockpit-project.org/) with [cockpit-podman](https://github.com/cockpit-project/cockpit-podman)

This will provide the operator with a basically configured Equinix Metal Alma host with a Cockput web interface hosted on the instance's public IP address. Cockpit can be used to then manage the podman containers through the Cockpit web portal.

## Networking

`not_ipmi_to_metal` containers can be placed on both Equinix Metal Layer-3 and Layer-2 networks. 

For customers that want to leverage the Equinix Metal Layer-3-as-a-Service networks, the "private" network can be an ideal network to host `not_ipmi_to_metal` containers, and containers can be hosted on private Elastic-IPs for customers who want a routeable IP per container.

For customers that want to leverage `not_ipmi_to_metal` on a Metal Layer-2 network, simply configure the host for the correct Layer-2 network attributes (VLANs + Customer Defined Layer-3), and `not_ipmi_to_metal` containers can serve their function out of customer managed networks.

## Self-built containers

Building from the Docker file should just follow each ecosystems toolchain, just checkout the repo and build against the Dockerfile.

`sudo docker -v build -t dlotterman/not_ipmi_to_metal:v3 ./`

Most users should be able to 

### docker

To pull the image from Docker Hub to the local registry:

`sudo docker pull dlotterman/not_ipmi_to_metal:v3`

Where `v3` is the version that comes from the `version` the `version` [file at the root of this repository](version).

Start the docker container:

```
export METAL_AUTH_TOKEN=YOUR_READ_WRITE_METAL_DOKEN && \
export METAL_INSTANCE_UUID=YOUR_METAL_INSTANCES_UUID && \
sudo docker run -d --name not_ipmi_to_metal_testv3 \
-e METAL_AUTH_TOKEN=$METAL_AUTH_TOKEN \
-e METAL_INSTANCE_UUID=$METAL_INSTANCE_UUID \
-p 127.0.0.1:623:623/udp \
dlotterman/not_ipmi_to_metal:v3
```

Where the `METAL_AUTH_TOKEN` environment variable is your [Equinix Metal Read / Write API token](https://metal.equinix.com/developers/api/authentication/#authentication) and the `METAL_INSTANCE_UUID` environment variable is the unique UUID of the Metal instance you would like to control, I.E the UUID of the box you want to power on / power off etc via IPMI.

Confirm the Container is running:

```
$ sudo docker ps
CONTAINER ID   IMAGE                             COMMAND                  CREATED         STATUS         PORTS                    NAMES
a13279437bd9   dlotterman/not_ipmi_to_metal:v3   "python3 not_ipmi_to…"   5 seconds ago   Up 4 seconds   127.0.0.1:623->623/udp   not_ipmi_to_metal_testv3
```

Confirm IPMI reachability:

```
$ ipmitool -H 127.0.0.1 -I lanplus -U admin -P password chassis power status
Chassis Power is off
```

## podman

Pull the container from Docker Hub:

```
$ sudo podman pull dlotterman/not_ipmi_to_metal
Trying to pull docker.io/dlotterman/not_ipmi_to_metal:v3...
Getting image source signatures
Copying blob e4f62a144629 skipped: already exists
Copying blob 3bc0ddfaace7 skipped: already exists
Copying blob c4cad43d3d2a skipped: already exists
Copying blob e57cc229acca skipped: already exists
Copying blob 3ddb78d65cbd skipped: already exists
Copying blob e0b25ef51634 skipped: already exists
Copying config 01cced0711 done
Writing manifest to image destination
Storing signatures
01cced0711cee19d63530252a3e8fb0e5379c961e45407c3e8c508f57dfc8fd5
```

Run the container:

```
export METAL_AUTH_TOKEN=YOUR_READ_WRITE_METAL_DOKEN && \
export METAL_INSTANCE_UUID=YOUR_METAL_INSTANCES_UUID && \
sudo podman run -d --name not_ipmi_to_metal_testv3 \
-e METAL_AUTH_TOKEN=$METAL_AUTH_TOKEN \
-e METAL_INSTANCE_UUID=$METAL_INSTANCE_UUID \
-p 127.0.0.1:623:623/udp \
dlotterman/not_ipmi_to_metal:v3
```


## systemd

`not_ipmi_to_metal` is a simple python daemon that can also easily be managed via a systemd unit file. Note it is strongly suggested to use a python virtualenv to avoid clashing with system level python dependencies.

`$ git clone https://github.com/dlotterman/not_ipmi_to_metal` 

`$ python3 -m venv ./ not_ipmi_to_metal`

```$ source bin/activate
(tmp)```

```
$ pip3 install --upgrade pip
Collecting pip
  Using cached pip-22.0.4-py3-none-any.whl (2.1 MB)
Installing collected packages: pip
  Attempting uninstall: pip
    Found existing installation: pip 20.0.2
    Uninstalling pip-20.0.2:
      Successfully uninstalled pip-20.0.2
Successfully installed pip-22.0.4
```

```
$ pip3 install -r requirements.txt
...
```


```
$ sudo cat > /etc/systemd/system/not_ipmi_to_metal_testv3.service <<EOF
[Unit]
Description=not_ipmi_to_metal_testv3
After=multi-user.target
[Service]
Type=simple
Restart=always
EnvironmentFile=/dev/shm/not_ipmi_to_metal_testv3
ExecStart=$PATH/not_ipmi_to_metal/bin/python3 $PATH/not_ipmi_to_metal/ipmi_to_metal/ipmi_to_metal.py
[Install]
WantedBy=multi-user.target
EOF
```

`$ sudo systemctl daemon-reload`

`$ systemctl enable not_ipmi_to_metal_testv3`
`$ systemctl start not_ipmi_to_metal_testv3`