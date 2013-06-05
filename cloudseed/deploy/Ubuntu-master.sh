#!/bin/bash

mkdir -p /etc/salt/pki
echo "{{ minion }}" > /etc/salt/minion
echo "{{ vm.cloudseed.master }}" > /etc/salt/master

echo "{{ vm.saltcloud.providers }}" > /etc/salt/cloud.providers; chmod 600 /etc/salt/cloud.providers
echo "{{ vm.saltcloud.profiles }}" > /etc/salt/cloud.profiles; chmod 600 /etc/salt/cloud.profiles
echo "{{ vm.saltcloud.config }}" > /etc/salt/cloud; chmod 600 /etc/salt/cloud
echo "{{ vm.saltcloud.private_key }}" > /etc/salt/cloud.pem; chmod 600 /etc/salt/cloud.pem


# add-apt-repository requires an additional dep and is in different packages
# on different systems. Although seemingly ubiquitous it is not a standard,
# and is only a convenience script intended to accomplish the below two steps
# doing it this way is universal across all debian and ubuntu systems.
echo deb http://ppa.launchpad.net/saltstack/salt/ubuntu `lsb_release -sc` main | tee /etc/apt/sources.list.d/saltstack.list
wget -q -O- "http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0x4759FA960E27C0A6" | apt-key add -

apt-get update
apt-get install -y git python-pip
pip install gitpython salt-cloud apache-libcloud
apt-get install -y -o DPkg::Options::=--force-confold salt-master
salt-key --gen-keys=master
cp master.pub /etc/salt/pki/master/minions/master
mkdir -p /etc/salt/pki/minion
mv master.pub /etc/salt/pki/minion/minion.pub
mv master.pem /etc/salt/pki/minion/minion.pem
apt-get install -y -o DPkg::Options::=--force-confold salt-minion
sleep 4; /usr/bin/salt "master" state.highstate
# minion will be started automatically by install
