#!/bin/bash
function jenkins_agent() {
   jenkinsAgentPrefix=$1

   echo "${executor_access_pub_keys}" >> /root/.ssh/authorized_keys

   #Register the node and create the work directory
   mkdir -p /home/$${jenkinsAgentPrefix}
   mkdir -p /home/jenkins/.ssh
   echo ${jenkins_pub_key} > /home/jenkins/.ssh/authorized_keys
   chown -R jenkins:jenkins /home/$${jenkinsAgentPrefix} /home/jenkins
}


#We sleep for a bit to allow the EIP to bind before registering the instance
sleep 120

#We loop through all agents to be registered on the VM NOTE: CANNOT PUT THIS COMMENT DIRECTLY ABOVE FOR LOOP OR INTERPOLATION DOESN'T WORK

%{~ for attributes in agent_attributes  ~}
   jenkins_agent ${attributes.prefix}

%{~ endfor ~}
