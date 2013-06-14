# Cloudseed

*Build locally with vagrant, then take that work and deploy it to the cloud.*

Cloudseed is basically a wrapper around salt (https://github.com/saltstack/salt)
and salt-cloud (https://github.com/saltstack/salt-cloud). It's Vagrant
abilities are provided courtesy of salty-vagrant (https://github.com/saltstack/salty-vagrant).

Cloudseed provides a default Vagrant setup with all the proper hookups to enable
your VM to run as a salt master an minion.

Additionally, it comes preconfigured to read your salt states from a public
git reporitory; no need to make copies of them all over the place.

Currently, Cloudseed only works with salt-cloud's **ec2** provider. Additionally
the only bootstrap script provided is for Ubuntu. Note however, that Cloudseed
floats on top of salt-cloud, which means anything that you can do with
salt-cloud is capable of being implemented under cloudseed. Specifically
the cloud provider extensions that cloudseed requires would just need to be
written.


## Requirements

**Keep in mind this software is not complete**

You are going to have to know some things about salt-cloud. Cloudseed was
orinigally built not using salt-cloud, but it seemed silly since salt-cloud
does a good job at handling all of the various cloud providers.

You can read more about salt-cloud here, specifically Profiles and Providers:
https://salt-cloud.readthedocs.org/en/latest/

### Known issues
Keep in mind this is pretty early on in the process of development. Yes, it
works. There appear to be a couple of corner cases when creating EC2 vm's
currently that can cause your *local->cloud* setup to not go as well.
Specifically I have gotten this issue more than a few times while testing:

https://github.com/saltstack/salt-cloud/issues/618


A lot of the logging is currently enabled. When you issue commands, you will
probably see some drama inder the hood.

Again, EC2 is the only provider currently setup to work.

Ubuntu is currently the only OS supported. Again, this is really just a matter
of authoring the extentions on the other providers.

Switching environments is not yet supported. It's just changing the symlink,
I just need to expose it.

Destroying your cloud setup is not yet implemented. You will need to do that
from the AWS dashboard for now. `cloudseed destroy` will be implemented soon.

**Vagrant** (http://www.vagrantup.com)

**Salty-Vagrant**
At the time of this writing, you will need to install the development version
of the salty-vagrant plugin. Why? We need to use the minion key presseding
feature which, as far as I can tell, is only available in the development
version. This is pretty simple to do, you can find instructions here:

https://github.com/saltstack/salty-vagrant#installing-from-source


**Cloudseed**
Salt and salt-cloud will both be installed when you install the Cloudseed lib,
which will need to be done from source:

### Getting started

#### TL;DR

```
cd ~/Projects
mkdir myproject && cd myproject
cloudseed init test

... edit cloudseed/test/vagrant/minion ...

vagrant up

... build your app ..

... edit cloudseed/test/salt/cloud.profiles ...
... edit cloudseed/test/salt/cloud.provders ...

cloudseed bootstrap
cloudseed deploy <profile>

... for kicks lets log into the master server ...

cloudseed ssh
```

#### Details

```
git clone https://github.com/cloudseed-project/cloudseed2.git cloudseed
cd cloudseed
python setup.py develop
```

With Cloudseed installed, lets start our project.

```
cd ~/Projects
mkdir myproject && cd myproject
cloudseed init test
```

Note here that `init` takes 1 argument. This is the environment you would like
to create. Cloudseed lets you initialize multiple environments for a single
project.

We have created an environment called `test`. In creating an environment it
has become our active environment as well.

Now lets see how the contents of our folder has changed:

```
ls -l

-rw-r--r--  1 user  staff  1043 Jun 14 05:17 Vagrantfile
drwxr-xr-x  4 user  staff   136 Jun 14 05:17 cloudseed

```

We have a Vagrantfile and a cloudseed directory. The Vagrantfile is all set up
to work salty-vagrant and cloudseed. Take a look. Remember you need to install
the development version of salty-vagrant.

Lets take a look in the clouseed folder now.

```
ls -l

lrwxr-xr-x  1 user  staff   60 Jun 14 05:17 current -> /Users/user/Projects/myproject/test
drwxr-xr-x  5 user  staff  170 Jun 14 05:17 test
```

We can see our environment, and that we have 1 symlink, `current` pointing
to it. Now lets look at our directory`test`:

```
ls -l

drwxr-xr-x  6 user  staff  204 Jun 14 05:17 salt
drwxr-xr-x  4 user  staff  136 Jun 14 05:17 srv
drwxr-xr-x  6 user  staff  204 Jun 14 05:17 vagrant
```

Starts to get a bit more interesting. Here we have the information to make
our environment go.

#### salt/
Represents what you would find in /etc/salt.
In our case we have the following files:

```
cloud  # Salt Cloud Configuration
cloud.profiles  # Salt Cloud Profiles
cloud.providers  # Salt Cloud Providers
master  # Salt master configuration
```
The contents of this folder will be synced to the cloud for you when you
`cloudseed bootstrap` or on demand with a `cloudseed sync`

Additionally, the Vagrantfile is already setup to share the master
configuration with the guest OS.

You **MUST** edit cloud.profiles and cloud.providers if you wish to deploy
to the cloud.

See the salt-cloud docs for details:
https://salt-cloud.readthedocs.org/en/latest/

One important thing to note here. For EC2 based deploys, salt-cloud
requires you to provide your private_key and key name as well as security
groups you would like your instances to belong to. Cloudseed provides some
conveneinces around this workflow.

If you do not define a private_key/key name in your provider, Cloudseed
will create one for you on AWS and save the key to
`cloudseed/test/salt/<key>.pem`.

Please note, you should not share this key with anyone. It is the key to access
your instances. Would be pretty unwise to hand it out.

Additionally, if you do not provide a securitygroup, Cloudseed will handle that
for you as well.

By default it will create an ssh security group and assign that to your master
as well as an application based security group that allows for open
communiction between all instances in the group.

Once it makes these changes, it will rewrite your local cloud.provider file
with the proper updates in place.

The minimum cloudseed based cloud.provider then look like this:

```
aws_test:
  id: <your AWS Key>
  key: <your AWS Secret>
  location: us-west-2
  provider: ec2
```

A cloud.profile that uses this provider would look like this:

```
master:
  provider: aws_test
  image: ami-8e109ebe
  size: Micro Instance
  script: Ubuntu-master
  ssh_username: ubuntu
```

A few things here:

You **MUST** create at least 1 profile with the name of `master`. This
represents the instance that will be created with a `cloudseed bootstrap`

Again, you **MUST** have a profile defined named **master**.

Note the use of `script` here. This is a cloudseed based script, not a
salt-cloud one. Salt-cloud contains it's own scripts for it's minions which
should be used for all of your profiles EXCLUDING your **master** profile.


#### srv/

Salt's file_roots by default look at /srv/salt and /srv/pillar. This is
where you put your pillar data and your salt states. This folder will be
synced to the cloud for you on `cloudseed bootstrap` or on demand with a
`cloudseed sync`. Additionally, the Vagrantfile is already setup to share
this location with the guest OS.


#### vagrant/

This is all the vagrant specific stuff you will need.

```
bootstrap-salt.sh  # custom salty-vagrant bootstrap (installs git, gitpython, python-pip)
minion  # Your salty-vagrant minion configuration - You will be editing this.
minion.pem  # Pressed keys for salty-vagrant, NEVER USE IN PRODUCTION EVER
minion.pub # Pressed keys for salty-vagrant, NEVER USE IN PRODUCTION EVER
```

The most import part here is the `minion` file. This is the file you will be
editing, mainily assigning roles, for your vagrant box to use. Additional
minion configuration for you cloud deploy will be done in
`cloudseed/test/salt/cloud.profiles`


Cloudseed's approach to minions is one of *just add grains*, in our case roles,
to tell our VM how it should be configured. For example:

`cloudseed/test/vagrant/minion`
```yaml
id: seed-minion.pub
master: localhost
grains:
  roles:
    - lamp
```

A quick aside, not the id and master settings here, this is vagrant and
salty-vagrant specific. You should not need to change these values. What we
are mainily instrested in is our custom grain declaration. Here we have
added 1 role: *lamp* which would represent a configuration for a lamp stack.

By default, cloudseed is hooked up to read it's states from
https://github.com/cloudseed-project/cloudseed-states, but you have a few
options here.

The way the salt master is configured, see `cloudseed/test/salt/master`, it
searches the local file_roots first **then** the github repository. Which means
you have the ability override anything you like by providing it in the
`cloudseed/test/srv/salt` folder. Remember this folder gets synced to the cloud
for you at bootstrap time or on demand, so if you include it, there,
it will be deployed.
