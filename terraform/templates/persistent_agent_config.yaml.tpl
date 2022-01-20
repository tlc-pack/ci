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

  %{~ for name,agent in persistent_agents ~}
  %{~ for attributes in agent.agent_attributes ~}
  %{~ for index, ip in agent.executor_ips ~}
  - permanent:
      labelString: "${attributes.labels}"
      launcher:
        ssh:
          credentialsId: "jenkins"
          host: "${ip}"
          port: 22
          sshHostKeyVerificationStrategy: "nonVerifyingKeyVerificationStrategy"
      name: "${attributes.prefix}.${ip}" 
      nodeDescription: "This agent lives on the VM ${name}-${index} and correspondingly\
        \ has index ${index}"
      nodeProperties:
      - envVars:
          env:
          - key: "CI_NUM_EXECUTORS"
            value: "${attributes.executors}"
      numExecutors: ${attributes.executors}
      remoteFS: "/home/${attributes.prefix}"
      retentionStrategy: "always"
  %{~ endfor ~}
  %{~ endfor ~}
  %{~ endfor ~}
