ARCH_ROOTFS=arch_rootfs
MANJARO_ROOTFS=manjaro_rootfs

IMAGE=gmoben/dev-env
MANJARO_TAG=manjaro
MANJARO_BASE_TAG=${MANJARO_TAG}-base

.PHONY: build manjaro manjaro_base

manjaro: manjaro_base _manjaro

_manjaro:
	docker build \
		-t ${IMAGE}:${MANJARO_TAG} \
		-f Dockerfile.manjaro \
		.

manjaro_base:
	@./bin/prepare_fs.sh manjaro ${MANJARO_ROOTFS}
	docker import ${MANJARO_ROOTFS}.tar ${IMAGE}:${MANJARO_BASE_TAG}
