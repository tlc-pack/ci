#! /usr/bin/env bash
set -xe
set -o pipefail


mkdir -p /var/jenkins/keys /var/jenkins/casc /var/jenkins/home /var/jenkins/persistent_data /var/jenkins/docs_home
chmod -R 755 /var/jenkins
chmod 700 /var/jenkins/keys
chown -R 1000:1000 /var/jenkins

# Create mount point
cat << EOF | sudo tee -a /etc/fstab
/dev/nvme1n1 /var/jenkins/persistent_data xfs discard,defaults,nofail 0 2
EOF

# Format disk
if [ "$(lsblk -n -o FSTYPE /dev/nvme1n1)" == "" ]; then
    mkfs.xfs /dev/nvme1n1
else
    echo "Disk already formatted"
fi
mount /var/jenkins/persistent_data
chown -R 1000:1000 /var/jenkins
