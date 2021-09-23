PROJECT_ID=jigentec-services
CLUSTER_NAME=image-detection-cluster
SERVICE_NAME=image-detection-detector
IMPORT_PATH=github.com/jigentec/${SERVICE_NAME}
GIT_COMMIT_HASH=$(shell git rev-parse HEAD | cut -c -16)
LOCAL_IMAGE=${PROJECT_ID}/${SERVICE_NAME}:${GIT_COMMIT_HASH}
GCR_IMAGE_LATEST=asia.gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest
GCR_IMAGE_COMMIT=asia.gcr.io/${LOCAL_IMAGE}

.PHONY: all deps creds docker deploy run clean

all: creds deps

deps:
	@echo "Updating requirements..."
	pip install requirements.txt

creds:
	gcloud config set project ${PROJECT_ID}
	gcloud config set container/cluster ${CLUSTER_NAME}
	gcloud container clusters get-credentials ${CLUSTER_NAME} \
		--zone asia-east1-b --project $(PROJECT_ID)

docker:
	@echo "Making Docker image..."
	#@[ -z "$(shell git status --porcelain)" ] || \
	#	(echo -e "\033[0;31mYou have uncommitted local changes.\033[0m" ; \
	#	 echo -e "\033[0;31mCommit/stash them before building.\033[0m" ; false)
	docker build -t ${LOCAL_IMAGE} .
	docker tag ${LOCAL_IMAGE} ${GCR_IMAGE_COMMIT}
	docker tag ${LOCAL_IMAGE} ${GCR_IMAGE_LATEST}

deploy: creds
	@echo "Deploying..."
	docker push ${GCR_IMAGE_COMMIT}
	docker push ${GCR_IMAGE_LATEST}
	kubectl set image deployment/${SERVICE_NAME} ${SERVICE_NAME}=${GCR_IMAGE_COMMIT}
	kubectl rollout status deployment/${SERVICE_NAME}

run:
	docker run -itd -p 5555\:5555 -p 5557\:5557 ${LOCAL_IMAGE}

clean:
	rm -f ./${SERVICE_NAME}


