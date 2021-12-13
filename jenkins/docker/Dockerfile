FROM jenkins/jenkins:lts
ENV JAVA_OPTS=-Djenkins.install.runSetupWizard=false
ENV JENKINS_OPTS=--sessionTimeout=10080
ENV CASC_JENKINS_CONFIG /var/jenkins_home/casc

USER root
RUN mkdir /provision
COPY plugins.txt /provision/required-plugins.txt
RUN bash -c 'install-plugins.sh </provision/required-plugins.txt'
ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

USER jenkins
