#!/bin/bash

mkdir -p /etc/salt/pki
echo "{{ minion }}" > /etc/salt/minion
echo "{{ vm.cloudseed.master }}" > /etc/salt/master

# add-apt-repository requires an additional dep and is in different packages
# on different systems. Although seemingly ubiquitous it is not a standard,
# and is only a convenience script intended to accomplish the below two steps
# doing it this way is universal across all debian and ubuntu systems.
echo deb http://ppa.launchpad.net/saltstack/salt/ubuntu `lsb_release -sc` main | tee /etc/apt/sources.list.d/saltstack.list
wget -q -O- "http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0x4759FA960E27C0A6" | apt-key add -

apt-get update
apt-get install -y git python-dev python-pip mongodb libzmq3-dev
pip install -e git://github.com/saltstack/salt-cloud.git#egg=develop
pip install gitpython apache-libcloud pymongo
apt-get install -y -o DPkg::Options::=--force-confold salt-master

# debugging purposes:
# this will be a pip install
# must start before the master comes online
sudo sh -c "git clone https://github.com/cloudseed-project/cloudseed2.git ~/cloudseed; cd ~/cloudseed && python setup.py develop; cloudseed agent"

salt-key --gen-keys=master
cp master.pub /etc/salt/pki/master/minions/master
mkdir -p /etc/salt/pki/minion
mv master.pub /etc/salt/pki/minion/minion.pub
mv master.pem /etc/salt/pki/minion/minion.pem
apt-get install -y -o DPkg::Options::=--force-confold salt-minion


#sleep 4; /usr/bin/salt "master" state.highstate
# minion will be started automatically by install
# install mongo and cloudseed and start the agent here


