environment              = "prod"
account_role_arn         = "arn:aws:iam::477529581014:role/Administrator"
public_subnet_ids = {
  "frontend-us-west-2a": "subnet-0548976da0eb119b8",
  "frontend-us-west-2b": "subnet-0fa03daf38e6b72a8",
  "frontend-us-west-2c": "subnet-0ab37ff3dbeb0e52b"
}
private_subnet_ids = {
  "agents-us-west-2a": "subnet-0dc8224b6f17d99a0",
  "agents-us-west-2b": "subnet-030ff1184253eb3dd",
  "agents-us-west-2c": "subnet-0700df0147c72cc6e"
}
vpc_id = "vpc-02d62f26d69ff4936"
executor_access_pub_keys = <<EOT
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBAsAaXCDJBISOQh8vdrUXyOSoQ2pfQuL57974OkuGbW
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBFZtISQW2MSKVj6wibk8nB4RBf4ZuoluJtBWmeWPoee
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQD8dz5526nwzfVCiQvqKCrH3o1rUq7HD84mlOO9/zsXuYY7iwcF/x3aeE24MIn5XfPZIye6iye+iEsN1rJQodamNCUA43G0TXS6Xj7T3fLAtU93eyceQIeuEjhDfSsFWeKpkZTRE0deloK9ioZs5oCI4NtjxnwZdk3gUQ0c+f1KAYvX5w9uOQXynMkuQcsCA6740eTVEr8ohp6TtafnVthUAK1acw+lDMXNSWC6FprFejTOFtwL+UQS2WjUAxijh0x7fU4VkNOqgfTnvU0DT86SYZ3tM+QAvKQSXPWuKkRgTC3rmjQBlv8E79bUwO1Mp4sL/VJj+8RcAC8C8F0duIHCNkYcXPBVDzP6FFZXt/SWzC89U23uw5I1n4x1YWQOl8Mz2/UaOScZ2voRvMc+bk7eMgdsPHKF0ao3u0ZRbgDwg+rf1R08Ed2PnZE2A3VLzH1ptSiImi74GemmjOZ9nWpeQ1UrVFHDNuRIeY9VUsvwzgxxq/K3mgIgs12lfVxkGsORvbcABLLVKaiM4rbtHLQ9SKqwk5OCSSvr3RUYSGrx5Y9nQvV0cB1nf6A7QE6dsF5vh1aJLwI89Eu3Fi/n53uZjgj1uF0/V+FjaQ8uY8bxm1sWrSFVrJ8augif3KL5vt9mOptbJL/0Az9GZzvoLf+U+bUJUJR7X35teC8o0u5IAQ==
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGaQeGRNUR4P2IEKd1x+Niqjfy1OjEjgwTQdXFe0nP7J
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQD8dz5526nwzfVCiQvqKCrH3o1rUq7HD84mlOO9/zsXuYY7iwcF/x3aeE24MIn5XfPZIye6iye+iEsN1rJQodamNCUA43G0TXS6Xj7T3fLAtU93eyceQIeuEjhDfSsFWeKpkZTRE0deloK9ioZs5oCI4NtjxnwZdk3gUQ0c+f1KAYvX5w9uOQXynMkuQcsCA6740eTVEr8ohp6TtafnVthUAK1acw+lDMXNSWC6FprFejTOFtwL+UQS2WjUAxijh0x7fU4VkNOqgfTnvU0DT86SYZ3tM+QAvKQSXPWuKkRgTC3rmjQBlv8E79bUwO1Mp4sL/VJj+8RcAC8C8F0duIHCNkYcXPBVDzP6FFZXt/SWzC89U23uw5I1n4x1YWQOl8Mz2/UaOScZ2voRvMc+bk7eMgdsPHKF0ao3u0ZRbgDwg+rf1R08Ed2PnZE2A3VLzH1ptSiImi74GemmjOZ9nWpeQ1UrVFHDNuRIeY9VUsvwzgxxq/K3mgIgs12lfVxkGsORvbcABLLVKaiM4rbtHLQ9SKqwk5OCSSvr3RUYSGrx5Y9nQvV0cB1nf6A7QE6dsF5vh1aJLwI89Eu3Fi/n53uZjgj1uF0/V+FjaQ8uY8bxm1sWrSFVrJ8augif3KL5vt9mOptbJL/0Az9GZzvoLf+U+bUJUJR7X35teC8o0u5IAQ==
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDJ/5rsSHbevazx3JJnAVQlOZdRg5l1PuR9JiFea2go5NqMfV4qrS1PnwkNTp/YzjLq1dbFw84QrKrMvAlGDHAOphr2CA+/FTMqrxlZyOwVEYg2Rna3ABetCkT+YuGuetP30UDEGiLSXg8v2/yvP7KjeQ8QJgx2RwI4C5Zhrz/bZ+nT5OkgNOpuBpB7n20YFpBfjs96q02/rXgEIx+UXyijcMTh8J/16z60pxvH05Ep0KTsZSe23WIW7CAl6QnLuCKYWEAfTNecuPBuQmKDpjYzxJBTjTo/gER6MbZjhM4wHyfitNKVvv3pSGUwoeCHcKf/BfBdFE+8KNNH3j0eIfUL
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDnzrWRUinQO2VOv0qCJF2QewA4ycUipWH53w/vMWO6V driazati
EOT

global_access_pub_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCPEfKqi1qHT6P3oTMwWYrS2w66bTUHIrT+41LptZbGMgzlZ91RA6npJlspf6HZ4OsK1hkFydS9SH3dF7HuND5rf1i7jS7btTzvtBAaD5I9WCnDV61ZGpVLNA38e9QCN5bx4k6wFIUYVQRqoFcGOMYyAbA2Fz7mp34dGzf+oY43viCFTgHxwUpDTWbNkGiNjvI+9hVfpk15oYz0QAL2326w4Hc0kQrqx8yAAdZbqitsqURLVixBAjVuUkc1WxxwPWy0k15xPgNJGKnjOT8u50XpEglQkuryYa47kOj7MtshR5PlSKzxTp1MlinnIMrrjd9ZR6pPI8r9zkUlUDeapBR1"

jenkins_pub_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBZvGmyspz5yaZ2n0H2U2XG8xULm2GYoT8Fo3qebI34v"

autoscaler_types = {
  "Prod-Autoscaler-Jenkins-CPU" = {
    image_family        = "jenkins-stock-agent"
    agent_instance_type = "c4.4xlarge"
    labels              = "CPU CPU-DOCKER CPU-docker-build"
    min_size            = 0
    max_size            = 90
  }
  "Prod-Autoscaler-Jenkins-GPU" = {
    image_family        = "jenkins-gpu-agent"
    agent_instance_type = "g4dn.xlarge"
    labels              = "TensorCore GPU Linux GPU-DOCKER GPUBUILD"
    min_size            = 0
    max_size            = 90
  }
  "Prod-Autoscaler-Jenkins-ARM" = {
    image_family        = "jenkins-stock-agent-arm"
    agent_instance_type = "m6g.4xlarge"
    labels              = "ARM"
    min_size            = 0
    max_size            = 90
  }
}

domain_name               = "ci.tlcpack.ai"
subject_alternative_names = ["docs.staging.tlcpack.ai"]
ebs_volume_size           = 500
