set -eux
set -o pipefail

apt install -y docker.io
systemctl enable docker
