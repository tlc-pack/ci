set -eux
# install Nvidia drivers and dependencies
curl -fSsl -O $BASE_URL/$NVIDIA_DRIVER_VERSION/NVIDIA-Linux-x86_64-$NVIDIA_DRIVER_VERSION.run
sh NVIDIA-Linux-x86_64-$NVIDIA_DRIVER_VERSION.run -s

#get the Nvidia container runtime
APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=1
curl -s -L https://nvidia.github.io/nvidia-container-runtime/gpgkey | \
  apt-key add -
distribution=$(. /etc/os-release;echo ${ID}${VERSION_ID})
curl -s -L https://nvidia.github.io/nvidia-container-runtime/$distribution/nvidia-container-runtime.list | \
  tee /etc/apt/sources.list.d/nvidia-container-runtime.list
apt update -y
apt install -y nvidia-container-runtime

cat << EOF > /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "2"
  },
  "default-runtime": "nvidia",
  "runtimes": {
  "nvidia": {
  "path": "/usr/bin/nvidia-container-runtime",
  "runtimeArgs": []
        }
  },
  "storage-driver": "overlay2"
}
EOF
