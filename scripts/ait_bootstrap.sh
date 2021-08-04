#!/bin/bash
function exitTrap(){
exitCode=$?
/opt/aws/bin/cfn-signal
--stack ${AWS::StackName}
--resource AitAutoScalingGroup
--region${AWS::Region} -e $exitCode || echo 'Failed to send Cloudformation Signal'
}

trap exitTrap EXIT
CONFIG_BUCKET_NAME=${ConfigBucketName}

function boostrap_aws_stuff(){
# rpms and stuff
yum install -y python3 wget unzip
wget -nv https://s3.amazonaws.com/cloudformation-examples/aws-cfn-bootstrap-py3-latest.tar.gz
wget -nv https://s3.amazonaws.com/amazoncloudwatch-agent/redhat/amd64/latest/amazon-cloudwatch-agent.rpm
curl  "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip " -o  "awscliv2.zip"
pip3 install aws-cfn-bootstrap-py3-latest.tar.gz

# directories
mkdir -p /opt/aws/bin
ln -s /usr/local/bin/cfn-* /opt/aws/bin

# Cloudwatch and SSM agent
sudo rpm -U ./amazon-cloudwatch-agent.rpm
yum install -y https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/linux_amd64/amazon-ssm-agent.rpm

# AWS CLI
unzip awscliv2.zip
./aws/install
}

function bootstrap_ait(){
# Install basic system tools needed for AIT Server
yum -y install @development python3 httpd mod_ssl vim
systemctl enable httpd
curl -SL https://github.com/stedolan/jq/relepermanently/deleteases/download/jq-1.5/jq-linux64  -o /usr/bin/jq
chmod +x /usr/bin/jq
python3 -m pip install virtualenv virtualenvwrapper
}

function install_ait_and_dependents(){
# Set variables for system install
PROJECT_HOME=/home/ec2-user
SETUP_DIR=/home/ec2-user/setup
USER=ec2-user
GROUP=ec2-user
AWS_REGION=${AWS::Region}

# Prepare python environment for AIT work
tee -a /root/.bashrc $PROJECT_HOME/.bashrc << EOM
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export WORKON_HOME=$PROJECT_HOME/.virtualenvs
export PROJECT_HOME=$PROJECT_HOME
export CONFIG_BUCKET_NAME=$CONFIG_BUCKET_NAME
source /usr/local/bin/virtualenvwrapper.sh
EOM
source /root/.bashrc


cat > $PROJECT_HOME/.virtualenvs/postactivate << EOM
if [ $VIRTUAL_ENV ==  "$PROJECT_HOME/.virtualenvs/ait" ]; then
export AIT_ROOT=$PROJECT_HOME/AIT-Core
export AIT_CONFIG=$PROJECT_HOME/AIT-Core/config/config.yaml
fi
EOM

mkvirtualenv ait
workon ait

# Pull assets, config, and secrets from s3/sm
mkdir -p $SETUP_DIR
cd $SETUP_DIR
/usr/local/aws-cli/v2/current/bin/aws --region $AWS_REGION s3 sync s3://$CONFIG_BUCKET_NAME/ait/ $SETUP_DIR/
/usr/local/aws-cli/v2/current/bin/aws --region $AWS_REGION secretsmanager get-secret-value --secret-id  "$AIT_SSL_KEY_SECRET_NAME " | jq -r ''.SecretString'' > $SETUP_DIR/server_ssl_key.pem
cd $PROJECT_HOME
/usr/local/aws-cli/v2/current/bin/aws --region $AWS_REGION s3 cp s3://${CONFIG_BUCKET_NAME}/modules/openmct.tgz - | tar- xz
# Install open-source AIT components
git clone https://github.com/NASA-AMMOS/AIT-Core.git $PROJECT_HOME/AIT-Core
cd $PROJECT_HOME/AIT-Core/
git checkout 2.0.1
pip install .
cp $SETUP_DIR/ait-example-config.yaml $PROJECT_HOME/AIT-Core/config/config.yaml
mkdir -p $PROJECT_HOME/AIT-Core/config/tlm
cp $PROJECT_HOME/AIT-Core/config/tlm.yaml $PROJECT_HOME/AIT-Core/config/tlm/tlm.yaml
cp $PROJECT_HOME/AIT-Core/config/ccsds_header.yaml $PROJECT_HOME/AIT-Core/config/tlm/ccsds_header.yaml
git clone https://github.com/NASA-AMMOS/AIT-GUI.git $PROJECT_HOME/AIT-GUI

cd $PROJECT_HOME/AIT-GUI/
git checkout 1e96dcb
pip install .

# Position ssl certificate & key for https
cp $SETUP_DIR/server_ssl_key.pem /etc/pki/tls/private/server_ssl_key.pem
cp $SETUP_DIR/server_ssl_cert.pem /etc/pki/tls/certs/server_ssl_cert.pem


# Copy necessary apache configs
cp $SETUP_DIR/httpd_ssl.conf /etc/httpd/conf.d/ssl.conf
cp $SETUP_DIR/httpd_proxy.conf /etc/httpd/conf.d/proxy.conf

# Install InfluxDB and data plugin
curl https://repos.influxdata.com/rhel/6/amd64/stable/influxdb-1.2.4.x86_64.rpm -o influxdb-1.2.4.x86_64.rpm
yum localinstall -y influxdb-1.2.4.x86_64.rpm

pip install influxdb
service influxdb start
systemctl enable influxdb

# Start AIT Server
nohup ait-server &

# Install and run OpenMCT
curl -q -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.38.0/install.sh | bash
tee >> $PROJECT_HOME/.bash_profile << EOM
export NVM_DIR= "$([ -z
"${!XDG_CONFIG_HOME-} " ] && printf %s  "${!HOME}/.nvm " || printf %s  "
${!XDG_CONFIG_HOME}/nvm ") "
[ -s  "$NVM_DIR/nvm.sh " ] && .  "$NVM_DIR/nvm.sh "
# This loads nvm
EOM
source $PROJECT_HOME/.bash_profile
nvm install 10

nvm use 10
cd $PROJECT_HOME/openmct
npm i node app.js -p 8081
systemctl start httpd
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:$SETUP_DIR/cloudwatch-agent-ait.json


# Give user ownership of all the things placed in project home during this setup script
chown -R $USER $PROJECT_HOME
chgrp -R $GROUP $PROJECT_HOME

deactivate
}

boostrap_aws_stuff
bootstrap_ait
install_ait_and_dependents
