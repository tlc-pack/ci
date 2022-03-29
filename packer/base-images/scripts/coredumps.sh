#!/bin/bash

set -eux
set -o pipefail

# directory for core dumps
mkdir -p /var/crash

# tell the kernel to put them in that directory
sysctl -w kernel.core_pattern=/var/crash/coredump-%e.%p.%h.%t

# remove the limit on core dump size
ulimit -c unlimited
