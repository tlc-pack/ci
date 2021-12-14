environment              = "staging"
executor_access_pub_keys = <<EOT
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBAsAaXCDJBISOQh8vdrUXyOSoQ2pfQuL57974OkuGbW
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBFZtISQW2MSKVj6wibk8nB4RBf4ZuoluJtBWmeWPoee
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQD8dz5526nwzfVCiQvqKCrH3o1rUq7HD84mlOO9/zsXuYY7iwcF/x3aeE24MIn5XfPZIye6iye+iEsN1rJQodamNCUA43G0TXS6Xj7T3fLAtU93eyceQIeuEjhDfSsFWeKpkZTRE0deloK9ioZs5oCI4NtjxnwZdk3gUQ0c+f1KAYvX5w9uOQXynMkuQcsCA6740eTVEr8ohp6TtafnVthUAK1acw+lDMXNSWC6FprFejTOFtwL+UQS2WjUAxijh0x7fU4VkNOqgfTnvU0DT86SYZ3tM+QAvKQSXPWuKkRgTC3rmjQBlv8E79bUwO1Mp4sL/VJj+8RcAC8C8F0duIHCNkYcXPBVDzP6FFZXt/SWzC89U23uw5I1n4x1YWQOl8Mz2/UaOScZ2voRvMc+bk7eMgdsPHKF0ao3u0ZRbgDwg+rf1R08Ed2PnZE2A3VLzH1ptSiImi74GemmjOZ9nWpeQ1UrVFHDNuRIeY9VUsvwzgxxq/K3mgIgs12lfVxkGsORvbcABLLVKaiM4rbtHLQ9SKqwk5OCSSvr3RUYSGrx5Y9nQvV0cB1nf6A7QE6dsF5vh1aJLwI89Eu3Fi/n53uZjgj1uF0/V+FjaQ8uY8bxm1sWrSFVrJ8augif3KL5vt9mOptbJL/0Az9GZzvoLf+U+bUJUJR7X35teC8o0u5IAQ==
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGaQeGRNUR4P2IEKd1x+Niqjfy1OjEjgwTQdXFe0nP7J
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQD8dz5526nwzfVCiQvqKCrH3o1rUq7HD84mlOO9/zsXuYY7iwcF/x3aeE24MIn5XfPZIye6iye+iEsN1rJQodamNCUA43G0TXS6Xj7T3fLAtU93eyceQIeuEjhDfSsFWeKpkZTRE0deloK9ioZs5oCI4NtjxnwZdk3gUQ0c+f1KAYvX5w9uOQXynMkuQcsCA6740eTVEr8ohp6TtafnVthUAK1acw+lDMXNSWC6FprFejTOFtwL+UQS2WjUAxijh0x7fU4VkNOqgfTnvU0DT86SYZ3tM+QAvKQSXPWuKkRgTC3rmjQBlv8E79bUwO1Mp4sL/VJj+8RcAC8C8F0duIHCNkYcXPBVDzP6FFZXt/SWzC89U23uw5I1n4x1YWQOl8Mz2/UaOScZ2voRvMc+bk7eMgdsPHKF0ao3u0ZRbgDwg+rf1R08Ed2PnZE2A3VLzH1ptSiImi74GemmjOZ9nWpeQ1UrVFHDNuRIeY9VUsvwzgxxq/K3mgIgs12lfVxkGsORvbcABLLVKaiM4rbtHLQ9SKqwk5OCSSvr3RUYSGrx5Y9nQvV0cB1nf6A7QE6dsF5vh1aJLwI89Eu3Fi/n53uZjgj1uF0/V+FjaQ8uY8bxm1sWrSFVrJ8augif3KL5vt9mOptbJL/0Az9GZzvoLf+U+bUJUJR7X35teC8o0u5IAQ==
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDJ/5rsSHbevazx3JJnAVQlOZdRg5l1PuR9JiFea2go5NqMfV4qrS1PnwkNTp/YzjLq1dbFw84QrKrMvAlGDHAOphr2CA+/FTMqrxlZyOwVEYg2Rna3ABetCkT+YuGuetP30UDEGiLSXg8v2/yvP7KjeQ8QJgx2RwI4C5Zhrz/bZ+nT5OkgNOpuBpB7n20YFpBfjs96q02/rXgEIx+UXyijcMTh8J/16z60pxvH05Ep0KTsZSe23WIW7CAl6QnLuCKYWEAfTNecuPBuQmKDpjYzxJBTjTo/gER6MbZjhM4wHyfitNKVvv3pSGUwoeCHcKf/BfBdFE+8KNNH3j0eIfUL
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDnzrWRUinQO2VOv0qCJF2QewA4ycUipWH53w/vMWO6V
EOT

global_access_pub_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCPEfKqi1qHT6P3oTMwWYrS2w66bTUHIrT+41LptZbGMgzlZ91RA6npJlspf6HZ4OsK1hkFydS9SH3dF7HuND5rf1i7jS7btTzvtBAaD5I9WCnDV61ZGpVLNA38e9QCN5bx4k6wFIUYVQRqoFcGOMYyAbA2Fz7mp34dGzf+oY43viCFTgHxwUpDTWbNkGiNjvI+9hVfpk15oYz0QAL2326w4Hc0kQrqx8yAAdZbqitsqURLVixBAjVuUkc1WxxwPWy0k15xPgNJGKnjOT8u50XpEglQkuryYa47kOj7MtshR5PlSKzxTp1MlinnIMrrjd9ZR6pPI8r9zkUlUDeapBR1"

jenkins_pub_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDOMv82cvJwNNTDsF+jeICCbkUhcdnKDxsNK7/TQ/jgnwfURArs8OkvvWAE6Cswb+haP9p5DJBLH8IOHmoPtcsjwM5bgaxRnauOS73k9OVuiBVOPwvy/10fiQKxZWSU23vuSRLe/nuugiAHp1Eg5Q94lfB4cTDJrbmPbZTcQqJp9fELw0tRRjwm92ZstW78kkTUqUMJ4jCjzxDdL8MPlAurKnuqmwd+BzsYz+TvCK6QeXCpi1H2+4DHvCrT1WkMUm6eFPKVYbtoPR4XvVCqmxwV6RF/dXqkmxEr+B6u/JZJBpZKRmVc0+ueGg6ZGrLPgGriEMqOqCc6EeRza0+NdZLSJA8M28MAwOwhTo99odfmXwy8K78TI9dMDp/xTP8O4yrzIu5sSqPTjUBuLlCQiqHxBNSM36zpIPPiZNvnYaESMO38eC/2Icsmq7Kl2dP4bI88gCTe1NwXZdP2uep5oX/R3OWc2+GYBksQT6Rcf777ytFqEJYdoIyH/PTd1qPDlgPVhZ5VYnOYXW2anhACYco7GZREnyH9tyFKN9uihUx7kQVk7izO4utPfT8obNMwPvhoAP4FomHS1l452VgzhpQ6SiZhXGg+t8/zpHQoMp4WGbCPf+RfFeSRQhH4zBeFyjYIicZG/VbWyOldZ6ciXez8WcHbNiBrWuembdoBOUeBXw=="

autoscaler_types = {
  "Staging-Autoscaler-Jenkins-CPU" = {
    image_family        = "jenkins-stock-agent"
    agent_instance_type = "r5.large"
    labels              = "CPU CPU-DOCKER CPU-docker-build"
    min_size            = 0
    max_size            = 30
  }
  "Staging-Autoscaler-Jenkins-GPU" = {
    image_family        = "jenkins-gpu-agent"
    agent_instance_type = "g4dn.xlarge"
    labels              = "TensorCore GPU Linux GPU-DOCKER GPUBUILD"
    min_size            = 0
    max_size            = 15
  }
  "Staging-Autoscaler-Jenkins-ARM" = {
    image_family        = "jenkins-stock-agent-arm"
    agent_instance_type = "m6g.4xlarge"
    labels              = "ARM"
    min_size            = 0
    max_size            = 4
  }
}
