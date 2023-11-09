#!/bin/bash
CODE_DIR=$PWD
DOCKERFILE=${CODE_DIR}/Dockerfile
TAG=tgi_test_demo
NAME=tgi_test_demo

# build docker image
#docker build --tag ${TAG} --file ${DOCKERFILE} .

# run docker container
docker run -d -it --rm --gpus all --ulimit memlock=-1 --ulimit stack=67108864  \
    -v ${CODE_DIR}/models:/workspace/models \
    -v ${CODE_DIR}:/workspace/ \
    --name ${NAME} \
    -p 5000:5000 \
    ${TAG}

# exec docker container
docker exec -it ${NAME} /bin/bash
