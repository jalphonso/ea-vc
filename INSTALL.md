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

AS REGULAR USER:  
cd  
sudo $(which pip3) install -U pip  
sudo $(which pip3) install juniper_datacenter_fabric-1.0.0-py3-none-any.whl  
echo 'eval "$(register-python-argcomplete fabric_init)"' >> .bashrc  
echo 'eval "$(register-python-argcomplete fabric_mgr)"' >> .bashrc  
. .bashrc  
mkdir -p inventory/dc1/host_vars  
mkdir -p inventory/dc1/group_vars  
mkdir -p inventory/dc1/config_change_logs  
mkdir -p inventory/dc1/configs  
ansible-galaxy install Juniper.junos  
