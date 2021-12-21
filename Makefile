PROJECT_ID=jigentec-services
SERVICE_NAME=yolo-on-cloud
GIT_COMMIT_HASH=$(shell git rev-parse HEAD | cut -c -16)
DOCKER_REPO=x24870/${SERVICE_NAME}

.PHONY: all deps creds docker deploy run clean

all: creds deps

deps:
	@echo "Updating requirements..."
	pip install requirements.txt

creds:
	gcloud config set project ${PROJECT_ID}

docker:
	@echo "Making Docker image..."
	@[ -z "$(shell git status --porcelain)" ] || \
		(echo -e "\033[0;31mYou have uncommitted local changes.\033[0m" ; \
		 echo -e "\033[0;31mCommit/stash them before building.\033[0m" ; false)
	docker build -t ${DOCKER_REPO} .
	docker push ${DOCKER_REPO}

deploy:
	nvidia-docker run -itd --network host ${DOCKER_REPO}

run:
	nvidia-docker run -it --network host ${DOCKER_REPO}

clean:
	rm -f ./${SERVICE_NAME}


