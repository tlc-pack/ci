#!/bin/bash
function jenkins_agent() {
   jenkinsAgentPrefix=$1
   jenkinsAgentLabels=$2
   jenkinsAgentCount=$3

   #We need to request a crumb before we can make other API requests to Jenkins head node
   JENKINS_CRUMB=$(curl --fail -0 -u "${JENKINS_USER_ID}:${JENKINS_TOKEN}" ''${JENKINS_URL}'/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,":",//crumb)' 2>/dev/null || echo "N/A")
   if [[ $${JENKINS_CRUMB} != "N/A" ]]; then
     echo "CSRF Enabled."
   else
     echo "CSRF not enabled."
   fi
  
   IP_ADDR=$(curl http://169.254.169.254/latest/meta-data/public-ipv4)
   TAG_NAME="Name"
   INSTANCE_ID="`wget -qO- http://instance-data/latest/meta-data/instance-id`"
   REGION="`wget -qO- http://instance-data/latest/meta-data/placement/availability-zone | sed -e 's:\([0-9][0-9]*\)[a-z]*\$:\\1:'`"
   HOST_NAME="`aws ec2 describe-tags --filters "Name=resource-id,Values=$${INSTANCE_ID}" "Name=key,Values=$${TAG_NAME}" --region $${REGION} --output=text | cut -f5`"

   INDEX=$${HOST_NAME##*-}
   NODE_NAME=$${jenkinsAgentPrefix}.$${IP_ADDR}

   echo "${executor_access_pub_keys}" >> /root/.ssh/authorized_keys

   #Register the node and create the work directory
   mkdir -p /home/$${jenkinsAgentPrefix}
   mkdir -p /home/jenkins/.ssh
   echo ${jenkins_pub_key} > /home/jenkins/.ssh/authorized_keys
   chown -R jenkins:jenkins /home/$${jenkinsAgentPrefix} /home/jenkins
   curl -L -s -o /dev/null -u "${JENKINS_USER_ID}:${JENKINS_TOKEN}" -H "Content-Type:application/x-www-form-urlencoded" -H "$${JENKINS_CRUMB}" -X POST -d 'json={"": ["hudson.plugins.sshslaves.SSHLauncher", "hudson.slaves.RetentionStrategy$Always"], "launcher": { "": "2","$class": "hudson.plugins.sshslaves.SSHLauncher","credentialsId": "jenkins","host": "'"$${IP_ADDR}"'","javaPath": "","jvmOptions": "","launchTimeoutSeconds": "","maxNumRetries": "","port": "22","prefixStartSlaveCmd": "","suffixStartSlaveCmd": "","retryWaitTime": "","sshHostKeyVerificationStrategy": { "$class": "hudson.plugins.sshslaves.verifiers.NonVerifyingKeyVerificationStrategy", "requireInitialManualTrust": false, "stapler-class": "hudson.plugins.sshslaves.verifiers.NonVerifyingKeyVerificationStrategy"},"stapler-class": "hudson.plugins.sshslaves.SSHLauncher"}, "name": "'"$$NODE_NAME"'", "nodeDescription": "This agent lives on the VM '"$${HOST_NAME}"' and correspondingly has index '"$${INDEX}"'",  "numExecutors": "'"$${jenkinsAgentCount}"'",  "remoteFS": "/home/'"$${jenkinsAgentPrefix}"'", "labelString": "'"$${jenkinsAgentLabels}"'", "mode": "NORMAL", "retentionStrategy": {"stapler-class": "hudson.slaves.RetentionStrategy$Always"}, "nodeProperties": {"stapler-class-bag": "true", "hudson-slaves-EnvironmentVariablesNodeProperty": {"env":[{"key":"CI_NUM_EXECUTORS","value":"'"$${jenkinsAgentCount}"'"}]}}, "type": "hudson.slaves.DumbSlave", "crumb": "'"$${JENKINS_CRUMB}"'"}' "${JENKINS_URL}/computer/doCreateItem?name=$${NODE_NAME}&type=hudson.slaves.DumbSlave"
}


#We sleep for a bit to allow the EIP to bind before registering the instance
sleep 120

#We loop through all agents to be registered on the VM NOTE: CANNOT PUT THIS COMMENT DIRECTLY ABOVE FOR LOOP OR INTERPOLATION DOESN'T WORK

%{~ for attributes in agent_attributes  ~}
   jenkins_agent ${attributes.prefix} "${attributes.labels}" ${attributes.executors}

%{~ endfor ~}
