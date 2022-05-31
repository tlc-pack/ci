set -eux
set -o pipefail

apt install -y \
    sysstat perf-tools-unstable linux-tools-common bpftrace \
    iotop smartmontools bpfcc-tools linux-headers-$(uname -r) \
    nicstat net-tools dnsutils ufw \
    jq vim tree cron htop curl nmap
