set -eux
# install Nvidia drivers and dependencies
apt install -y linux-headers-$(uname -r)
curl -fSsl -O $BASE_URL/$NVIDIA_DRIVER_VERSION/NVIDIA-Linux-x86_64-$NVIDIA_DRIVER_VERSION.run
sh NVIDIA-Linux-x86_64-$NVIDIA_DRIVER_VERSION.run -s

# install nvidia-container-toolkit (replaces deprecated nvidia-container-runtime)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
apt update -y
apt install -y nvidia-container-toolkit
cat << EOF > /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "2"
  },
  "storage-driver": "overlay2"
}
EOF

nvidia-ctk runtime configure --runtime=docker --set-as-default
