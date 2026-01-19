FROM jenkins/jenkins:2.528.3-lts-jdk17
ENV JAVA_OPTS=-Djenkins.install.runSetupWizard=false
ENV JENKINS_OPTS=--sessionTimeout=10080
ENV CASC_JENKINS_CONFIG=/var/jenkins_home/casc

USER root
RUN mkdir /provision
COPY plugins.txt /provision/required-plugins.txt
RUN curl https://github.com/jenkinsci/plugin-installation-manager-tool/releases/download/2.13.0/jenkins-plugin-manager-2.13.0.jar -o jenkins-plugin-manager.jar -L
RUN java -jar jenkins-plugin-manager.jar -f /provision/required-plugins.txt --verbose
ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

USER jenkins
