# IoMBian Tunnels Handler

This service creates SSH tunnels and, using the [IoMBian Configurator platform](https://iombian-configurator.web.app/), allows the device to be controlled and managed remotely, from outside the local network.

> Warning: the service assumes that the boringproxy binary file is properly installed and available in one of the most common binary folders (/usr/bin, /usr/sbin, /usr/local/bin or /usr/local/sbin).


## Installation

- Define project name in an environment variable:

```shell
PROJECT_NAME=iombian-tunnels-handler
```

- Clone the repo into a temp folder:

```shell
git clone https://github.com/Tknika/${PROJECT_NAME}.git /tmp/${PROJECT_NAME} && cd /tmp/${PROJECT_NAME}
```

- Create the installation folder and move the appropiate files (edit the user):

```shell
sudo mkdir /opt/${PROJECT_NAME}
```

```shell
sudo cp requirements.txt /opt/${PROJECT_NAME}
```

```shell
sudo cp -r src/* /opt/${PROJECT_NAME}
```

```shell
sudo cp systemd/${PROJECT_NAME}.service /etc/systemd/system/
```

```shell
sudo chown -R iompi:iompi /opt/${PROJECT_NAME}
```

- Create the virtual environment and install the dependencies:

```shell
cd /opt/${PROJECT_NAME}
```

```shell
python3 -m venv venv
```

```shell
source venv/bin/activate
```

```shell
pip install --upgrade pip
```

```shell
pip install -r requirements.txt
```

- Start the script

```shell
sudo systemctl enable ${PROJECT_NAME}.service && sudo systemctl start ${PROJECT_NAME}.service
```


## Author

(c) 2022 [Aitor Iturrioz Rodríguez](https://github.com/bodiroga)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
