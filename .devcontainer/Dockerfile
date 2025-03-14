FROM ubuntu:22.04

# sys
RUN apt update && apt upgrade -y
RUN apt install -y software-properties-common wget build-essential

RUN apt install python3-launchpadlib -y
RUN rm -rf ~/.launchpadlib/api.launchpad.net/cache/

RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py

# git
RUN apt install -y git

# numpy
RUN pip3 install numpy

# opencv
RUN pip3 install opencv-contrib-python-headless

# aiohttp
RUN pip3 install aiohttp
