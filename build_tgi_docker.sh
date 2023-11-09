#!/bin/bash
CODE_DIR=$PWD
DOCKERFILE=${CODE_DIR}/Dockerfile
TAG=tgi_test_demo
NAME=tgi_test_demo

# build docker image
docker build --tag ${TAG} --file ${DOCKERFILE} .
