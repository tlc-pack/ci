jenkins:
  nodes:
  - permanent:
      labelString: "doc"
      launcher:
        ssh:
          credentialsId: "jenkins"
          host: "jenkins-agent"
          port: 22
          sshHostKeyVerificationStrategy: "nonVerifyingKeyVerificationStrategy"
      name: "docs"
      numExecutors: 1
      remoteFS: "/var/jenkins_home"
      retentionStrategy: "always"

  %{~ for name,attributes in additional_agents ~}
  - permanent:
      labelString: "${attributes.labels}"
      launcher:
        ssh:
          credentialsId: "jenkins"
          host: "${attributes.host}"
          port: 22
          sshHostKeyVerificationStrategy: "nonVerifyingKeyVerificationStrategy"
      name: "${name}" 
      numExecutors: ${attributes.num_executors}
      remoteFS: "${attributes.remote_fs}"
      retentionStrategy: "always"
  %{~ endfor ~}
