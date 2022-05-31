#! /usr/bin/env bash
mkdir -p /home/jenkins/.ssh
touch /home/jenkins/.profile
echo "CI_NUM_EXECUTORS=1" >> /home/jenkins/.ssh/environment
chmod 700 /home/jenkins/.ssh/environment
echo ${jenkins_pub_key} >> /home/jenkins/.ssh/authorized_keys
chown -R jenkins:jenkins /home/jenkins
echo "${executor_access_pub_keys}" >> /root/.ssh/authorized_keys
echo "PermitUserEnvironment yes" >> /etc/ssh/sshd_config
systemctl restart sshd
