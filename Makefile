.PHONY: build debug test run

IMAGE_NAME ?= ghcr.io/ministryofjustice/analytical-platform-scheduler
IMAGE_TAG  ?= local

debug: build
	docker run --rm -it --publish 3000:3000 --entrypoint /bin/sh $(IMAGE_NAME):$(IMAGE_TAG)

run: build
	docker run --rm -it --publish 3000:3000 $(IMAGE_NAME):$(IMAGE_TAG)

test: build
	container-structure-test test --platform linux/amd64 --config test/container-structure-test.yml --image $(IMAGE_NAME):$(IMAGE_TAG)

build:
	@ARCH=`uname --machine`; \
	case $$ARCH in \
	aarch64 | arm64) \
		echo "Building on $$ARCH architecture"; \
		docker build --platform linux/amd64 --file Dockerfile --tag $(IMAGE_NAME):$(IMAGE_TAG) . ;; \
	*) \
		echo "Building on $$ARCH architecture"; \
		docker build --file Dockerfile --tag $(IMAGE_NAME):$(IMAGE_TAG) . ;; \
	esac
