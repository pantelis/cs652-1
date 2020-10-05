#!/bin/bash
#This script should set up pip and Ryu properly
#This script should be run immediately after importing the Mininet OVF as a new VM


#sudo apt update && sudo apt upgrade -y
#There will be user intervention required for:
# 1) Configuring wireshark-common (0%)
# 2) The sudoers file has been modified (88%)
# 3) Configuring grub-pc (95%)

sudo apt update && sudo DEBIAN_FRONTEND=noninteractive apt -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" dist-upgrade
#Accomplishes 100% non-interactive `sudo apt update && sudo apt upgrade -y`

sudo apt install python-pip python-dev libxml2-dev libxslt-dev zlib1g-dev -y
#Dependencies for Ryu

git clone https://github.com/faucetsdn/ryu.git
sudo python ./ryu/setup.py install
#Runs the setup script from the ryu directory

sudo pip install -r ./ryu/tools/pip-requires
#In the Ryu source code, there is a file in the tools directory called pip-requires
#This contains additional requirements for pip packages to be installed


#Several of the pip-requirements fail. These are handled individually below.

#oslo.config error
#These steps will handle oslo.config error by manually installing a working version
wget https://files.pythonhosted.org/packages/69/2a/727e8c396f831e51f79486e88588944f2553e43335d07cc1542442ac897a/oslo.config-2.5.0.tar.gz
tar -xzf oslo.config-2.5.0.tar.gz && rm oslo.config-2.5.0.tar.gz
sudo python ./oslo.config-2.5.0/setup.py install

#webob Distribution Not Found
#webob>=1.2
sudo pip install 'webob==1.2'

#tinyrpc Distribution Not Found
#tinyrpc==0.9.4
sudo pip install 'tinyrpc==0.9.4'

#routes Distribution Not Found
sudo pip install routes

#ovs Distribution Not Found
#ovs>=2.6.0
sudo pip install 'ovs==2.6.0'

#netaddr Distribution Not Found
sudo pip install netaddr

#msgpack Distribution Not Found
#msgpack>=0.3.0,<1.0.0
#msgpack versions available to use: 0.5.0, 0.5.1, 0.5.2, 0.5.3, 0.5.4, 0.5.5, 0.5.6, 0.6.0, 0.6.1, 0.6.2
sudo pip install 'msgpack==0.5.0'

#eventlet Distribution Not Found
#eventlet>=0.18.2,!=0.18.3,!=0.20.1,!=0.21.0,!=0.23.0
sudo pip install 'eventlet==0.18.2'

#greenlet
#greenlet>=0.3
wget https://files.pythonhosted.org/packages/9f/29/c8d0b051afacd0108c26a89824a13fa041299b61e8d9e50a6a35e25c4ec1/greenlet-0.3.tar.gz
tar -xzf greenlet-0.3.tar.gz && rm greenlet-0.3.tar.gz
sudo python ./greenlet-0.3/setup.py install

#stevedore Distribution Not Found
#stevedore>=1.5.0
sudo pip install 'stevedore==1.5.0'

#zipp Distribution Not Found
#zipp>=0.4
sudo pip install 'zipp==0.4'


#At this point, you can finally run `ryu-manager` without any additional Distribution Not Found errors
ryu-manager ./ryu/ryu/app/simple_switch.py
#
#Can run this command in concert with, in another terminal:
#
#sudo mn --topo single,3 --mac --switch ovsk --controller remote
#
#
#Once the mininet terminal comes up, run:
#
#pingall
