MANJARO_ROOTFS=manjaro_rootfs

IMAGE=gmoben/dev-env

BASE=${IMAGE}:base
MINIMAL=${IMAGE}:minimal
EMACS=${IMAGE}:emacs
WITH_USER=${IMAGE}:${USER}

.PHONY: clean build base minimal emacs full run run_minimal run_emacs

clean:
	sudo rm -rf ${MANJARO_ROOTFS}*

build:
	docker pull ${BASE} || ${MAKE} base
	${MAKE} minimal

push:
	docker push ${BASE}

base:
	@./bin/prepare_fs.sh manjaro ${MANJARO_ROOTFS}
	docker import ${MANJARO_ROOTFS}.tar ${BASE}

minimal:
	docker build \
		--build-arg user=${USER} \
		-t ${MINIMAL} \
		-t ${WITH_USER} \
		-f Dockerfile.minimal \
		.

emacs:
	docker build \
		--build-arg user=${USER} \
		-t ${EMACS} \
		-f Dockerfile.emacs \
		.

full: base minimal emacs

run: run_user

run_user:
	docker run --rm -it \
		-v ${HOME}/.gnupg:${HOME}/.gnupg \
		-v ${HOME}/.ssh:${HOME}/.ssh \
		${WITH_USER}

run_emacs:
	docker run --rm -it \
		-v ${HOME}/.gnupg:${HOME}/.gnupg \
		-v ${HOME}/.ssh:${HOME}/.ssh \
		${EMACS}
