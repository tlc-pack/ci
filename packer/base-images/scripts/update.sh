set -eux
set -o pipefail

apt-get update -y
apt-get upgrade -y
apt-get install -y unattended-upgrades apt-listchanges\
    gpg apt-transport-https software-properties-common \
    ca-certificates
