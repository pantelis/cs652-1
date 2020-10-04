#!/bin/bash
#This script should set up pip and Ryu properly
#This script should be run immediately after importing the Mininet OVF as a new VM

sudo apt update && sudo apt upgrade -y
#There will be user intervention required for:
# 1) Configuring wireshark-common
# 2) The sudoers file has been modified
# 3) Configuring grub-pc

sudo apt install python-pip -y
#This installs pip, which will be used to install Ryu

sudo apt install python-dev libxml2-dev libxslt-dev zlib1g-deb -y
#Dependencies for Ryu

git clone https://github.com/faucetsdn/ryu.git
cd ryu
#Clones the source code for Ryu from GitHub and changes into that directory

sudo python ./setup.py install
#Runs the setup script from the ryu directory

sudo pip install -r ./tools/pip-requires
#In the Ryu source code, there is a file in the tools directory called pip-requires
#This contains additional requirements for pip packages to be installed

#oslo.config error
#These steps will handle oslo.config error by manually installing a working version
cd ../ 
#get out of the ryu directory

wget https://files.pythonhosted.org/packages/69/2a/727e8c396f831e51f79486e88588944f2553e43335d07cc1542442ac897a/oslo.config-2.5.0.tar.gz
tar -xzf oslo.config-2.5.0.tar.gz && rm oslo.config-2.5.0.tar.gz
cd oslo.config-2.5.0
sudo python ./setup.py install
cd ../
#get out of the oslo.config-2.5.0 directory

#Individual problems
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

#stevedore Distribution Not Found
#stevedore>=1.5.0
sudo pip install 'stevedore==1.5.0'

#zipp Distribution Not Found
#zipp>=0.4
sudo pip install 'zipp==0.4'


#At this point, you can finally run `ryu-manager` without any additional Distribution Not Found errors
#Uncomment to test:
#
#ryu-manager ./ryu/ryu/app/simple_switch.py
#
#
#Can run this command in concert with, in another terminal:
#
#sudo mn --topo single,3 --mac --switch ovsk --controller remote
#
#
#Once the mininet terminal comes up, run:
#
#pingall