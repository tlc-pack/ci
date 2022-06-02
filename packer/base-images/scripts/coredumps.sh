#!/bin/bash

set -eux
set -o pipefail

# directory for core dumps
mkdir -p /var/crash

# tell the kernel to put them in that directory
echo "
kernel.core_pattern=/var/crash/coredump-%e.%p.%h.%t
" >> /etc/sysctl.conf

# turn off apport
echo "
enabled=0
" > /etc/default/apport
systemctl disable apport.service
systemctl mask apport.service

# remove the limit on core dump size
echo "
*    soft    core unlimited
*    hard    core unlimited

" > /etc/security/limits.d/core.conf
