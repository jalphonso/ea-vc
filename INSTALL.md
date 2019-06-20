CentOS 7.5 installation instructions

AS ROOT:
yum install gcc openssl-devel bzip2-devel libffi-devel wget
cd /usr/src
wget https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tgz
tar xzf Python-3.7.3.tgz
cd Python-3.7.3
./configure --enable-optimizations
make altinstall
cd /usr/local/bin
ln -s pip3.7 pip3
ln -s python3.7 python3
ln -s $(which python3) /usr/bin/python3
$(which pip3) install -U pip
$(which pip3) install selinux
$(which pip3) install juniper_datacenter_fabric-1.0.0-py3-none-any.whl
ansible-galaxy install Juniper.junos

AS REGULAR USER:
echo 'eval "$(register-python-argcomplete fabric_init)"' >> .bashrc
echo 'eval "$(register-python-argcomplete fabric_mgr)"' >> .bashrc
. .bashrc
mkdir -p inventory/dc1/host_vars
mkdir -p inventory/dc1/group_vars
mkdir -p inventory/dc1/config_change_logs
mkdir -p inventory/dc1/configs

vim inventory/dc1/group_vars/all.yml
*place the following fields in there updating values appropriate to your environment*
Lab_user_encrypted_pw: "$6$zIKJNefJ$amwbrri1wHu5ME3WtL0tv6bOKt3U5u/VLEV3nDdGErC893RdHfQVs6DLIZEiIh3cIy8xEN7X8yaqjuY06gfD60"
root_user_encrypted_pw: "$6$JNow/UvT$Tu5aPwN5pVPrJ8lEDNuXb/PrhFC9AqI/EAQfYQdizjH3asyfItiuyw7W6hVm0fj8PQ5rjKmnnzNQ8/yypcCuk0"
netconf_port: "830"
device_timeout: 60

*Note: netconf_port value needs to be quoted to avoid warning. device_timeout is an integer so no quotes*