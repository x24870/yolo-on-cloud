ARG BASE_IMAGE=nvidia/cuda:11.4.2-cudnn8-devel-ubuntu20.04
FROM $BASE_IMAGE AS builder
LABEL maintainer="Rick Yeh <yeh@jigentec.com>"

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update \
      && apt-get install --no-install-recommends --no-install-suggests -y gnupg2 ca-certificates \
            git build-essential libopencv-dev \
      && rm -rf /var/lib/apt/lists/*

COPY configure.sh /tmp/

ARG SOURCE_BRANCH="darknet_yolo_v4_pre"
ENV SOURCE_BRANCH $SOURCE_BRANCH

ARG SOURCE_COMMIT="bef28445e57cd560fa3d0a24af98a562d289135b"
ENV SOURCE_COMMIT $SOURCE_COMMIT

ARG CONFIG="gpu-cv"
ENV CONFIG $CONFIG

RUN git clone https://github.com/AlexeyAB/darknet.git && cd darknet \
      #&& git checkout $SOURCE_BRANCH \
      #&& git reset --hard $SOURCE_COMMIT \
      && /tmp/configure.sh $CONFIG && make \
      && cp darknet /usr/local/bin \
      && cp libdarknet.so /usr/local/bin \
      && cd .. && rm -rf darknet

FROM nvidia/cuda:11.2.2-cudnn8-runtime-ubuntu20.04
LABEL maintainer="Rick Yeh <yeh@jigentec.com>"

ENV DEBIAN_FRONTEND noninteractive

ARG SOURCE_BRANCH=unspecified
ENV SOURCE_BRANCH $SOURCE_BRANCH

ARG SOURCE_COMMIT=unspecified
ENV SOURCE_COMMIT $SOURCE_COMMIT

RUN apt-get update \
      && apt-get install --no-install-recommends --no-install-suggests -y libopencv-highgui4.2 \
      && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/bin/darknet /usr/local/bin/darknet
COPY --from=builder /usr/local/bin/libdarknet.so /usr/local/bin/libdarknet.so

# mlserver env setup
WORKDIR /usr/src/app

RUN apt-get update \
	&& apt-get install -y software-properties-common \
	&& add-apt-repository ppa:deadsnakes/ppa \
	&& apt-get install -y python3.9 \
	&& apt-get install -y python3-pip \
	&& apt-get install -y python3-opencv

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

# only copy mlserver to container
COPY ./mlserver .
ENTRYPOINT ["python3", "./mlserverclient.py"]
