set -eux
set -o pipefail

apt install -y jenkins-job-builder
useradd jenkins
mkdir /home/jenkins
chown jenkins:jenkins /home/jenkins

usermod -aG docker jenkins
usermod -aG docker root
usermod -aG docker ubuntu

#Build essentials like make and gcc
apt install -y build-essential
apt install -y python3 python3-pip
pip install -q poetry launchpadlib
apt install -y openjdk-8-jre-headless
pip install docker

#echo new cron into cron file
echo '0 * * * * docker system prune --volumes --force' | crontab

docker network create jenkin



