# IoMBian Tunnels Handler

This service creates SSH tunnels and, using the [IoMBian Configurator platform](https://iombian-configurator.web.app/), allows the device to be controlled and managed remotely, from outside the local network.

> Warning: the service assumes that the boringproxy binary file is properly installed and available in one of the most common binary folders (/usr/bin, /usr/sbin, /usr/local/bin or /usr/local/sbin).


## Installation

- Clone the repo into a temp folder:

> ```git clone https://github.com/Tknika/iombian-tunnels-handler.git /tmp/iombian-tunnels-handler && cd /tmp/iombian-tunnels-handler```

- Create the installation folder and move the appropiate files (edit the user):

> ```sudo mkdir /opt/iombian-tunnels-handler```

> ```sudo cp requirements.txt /opt/iombian-tunnels-handler```

> ```sudo cp -r src/* /opt/iombian-tunnels-handler```

> ```sudo cp systemd/iombian-tunnels-handler.service /etc/systemd/system/```

> ```sudo chown -R iompi:iompi /opt/iombian-tunnels-handler```

- Create the virtual environment and install the dependencies:

> ```cd /opt/iombian-tunnels-handler```

> ```python3 -m venv venv```

> ```source venv/bin/activate```

> ```pip install --upgrade pip```

> ```pip install -r requirements.txt```

- Start the script

> ```sudo systemctl enable iombian-tunnels-handler.service && sudo systemctl start iombian-tunnels-handler.service```


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