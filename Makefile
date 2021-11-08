PROJECT_ID=jigentec-services
IMPORT_PATH=github.com/jigentec/${SERVICE_NAME}
GIT_COMMIT_HASH=$(shell git rev-parse HEAD | cut -c -16)
LOCAL_IMAGE=${PROJECT_ID}/${SERVICE_NAME}:${GIT_COMMIT_HASH}

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
	docker build -t x24870/yolo-on-cloud .

deploy:
	nvidia-docker run -itd --network host ${LOCAL_IMAGE}

run:
	nvidia-docker run -it --network host ${LOCAL_IMAGE}

clean:
	rm -f ./${SERVICE_NAME}


