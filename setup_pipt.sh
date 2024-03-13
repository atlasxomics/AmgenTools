#!/bin/bash
mkfifio /root/pipe/the_pipe
while true; do eval "$(cat /root/pipe/the_pipe)"; done