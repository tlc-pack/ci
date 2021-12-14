set -eux
set -o pipefail

sh -c "echo 'deb [signed-by=/usr/share/keyrings/datadog-archive-keyring.gpg] https://apt.datadoghq.com/ stable 7' > /etc/apt/sources.list.d/datadog.list"
touch /usr/share/keyrings/datadog-archive-keyring.gpg

curl https://keys.datadoghq.com/DATADOG_APT_KEY_CURRENT.public | gpg --no-default-keyring --keyring /usr/share/keyrings/datadog-archive-keyring.gpg --import --batch
curl https://keys.datadoghq.com/DATADOG_APT_KEY_382E94DE.public | gpg --no-default-keyring --keyring /usr/share/keyrings/datadog-archive-keyring.gpg --import --batch
curl https://keys.datadoghq.com/DATADOG_APT_KEY_F14F620E.public | gpg --no-default-keyring --keyring /usr/share/keyrings/datadog-archive-keyring.gpg --import --batch

apt-get update
apt-get install -y datadog-agent
mv /etc/datadog-agent/datadog.yaml.example /etc/datadog-agent/datadog.yaml
systemctl enable datadog-agent.service
