jenkins:
  clouds: 
  
  %{~ for name,attributes in fleet_attributes  ~}
  - ec2Fleet:
        addNodeOnlyIfRunning: false
        alwaysReconnect: false
        cloudStatusIntervalSec: 10
        computerConnector:
          sSHConnector:
            credentialsId: "jenkins"
            launchTimeoutSeconds: 60
            maxNumRetries: 10
            port: 22
            retryWaitTime: 15
            sshHostKeyVerificationStrategy: "nonVerifyingKeyVerificationStrategy"
        disableTaskResubmit: false
        fleet: ${name}
        idleMinutes: 1
        initOnlineCheckIntervalSec: 15
        initOnlineTimeoutSec: 180
        labelString: "${attributes.labels}"
        maxSize: ${attributes.max_size}
        maxTotalUses: -1
        minSize: ${attributes.min_size}
        name: "${name}"
        noDelayProvision: false
        numExecutors: 1
        oldId: "803939ae-c6f8-4c7a-8386-0d1a9af631ad"
        privateIpUsed: false
        region: "us-west-2"
        restrictUsage: false
        scaleExecutorsByWeight: false
  
  %{~ endfor ~}
