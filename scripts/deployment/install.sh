#!/bin/bash

imageFile="$GO_PIPELINE_NAME.tar"
imageVersion=$GO_PIPELINE_COUNTER
imageName="unicef/$GO_PIPELINE_NAME"
deployFolder=$1




#Ensure that Docker is installed
if [ ! -f /usr/local/bin/docker ]; then
    #install docker
    apt-get update
    apt-get -y install docker.io
    ln -sf /usr/bin/docker.io /usr/local/bin/docker
    sed -i '$acomplete -F _docker docker' /etc/bash_completion.d/docker.io
    update-rc.d docker.io defaults

    #install DOCKER-COMPOSE
    curl -L https://github.com/docker/compose/releases/download/1.2.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose

fi

mkdir -p /opt/app/eums

#stop the docker composition
if [ -f /opt/app/eums/docker-compose.yml ]; then
    cd /opt/app/eums
    docker-compose stop
fi

#install the images
scripts/install-image-eums.sh
scripts/install-image-contacts.sh

#deploy updates to the docker-compose file
cp scripts/deployment/docker-compose.yml /opt/app/eums/docker-compose.yml

#start the docker compositon
cd /opt/app/eums
docker-compose start
