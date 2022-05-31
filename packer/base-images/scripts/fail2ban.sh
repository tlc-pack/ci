set -eux
set -o pipefail
    apt-get install -y fail2ban
cat << EOF >> /etc/fail2ban/jail.local
[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
EOF
        systemctl enable fail2ban
