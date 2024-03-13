#!/bin/bash
mkfifo /root/PortableAtlasTools/pipe/the_pipe
docker network create atx-cloud
cd /root/PortableAtlasTools/dockerfiles
docker-compose up -d
while true; do eval "$(cat /root/pipe/the_pipe)"; done