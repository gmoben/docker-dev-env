#/bin/env bash

readonly BIN_DIR=$(cd "$(dirname "$0")" > /dev/null && pwd -P)
source "${BIN_DIR}/utils.sh"


function manjaro() {
    expect_manjaro

    rootfs=$1
    if [[ $rootfs == "" ]]; then
	rootfs=tmp
    fi

    newdir $rootfs
    sudo basestrap -cdGM $rootfs filesystem base-devel pacaur gnupg

    # sudo wget -O $rootfs/usr/bin/systemctl https://raw.githubusercontent.com/gdraheim/docker-systemctl-replacement/master/files/docker/systemctl.py && sudo chmod a+x $rootfs/usr/bin/systemctl

    if [[ -f $rootfs.tar ]]; then
	sudo rm -rf $rootfs.tar
    fi

    sudo tar -C $rootfs -cf $rootfs.tar .
    sudo rm -rf $rootfs
}

function build_fs() {
    if [[ $1 = "manjaro" ]]; then
	manjaro $2
    else
	echo "Unknown distro $1"
	exit 1
    fi
}

function main() {
    if [[ $1 == "" ]]; then
	echo "Usage: prepare_fs.sh <distro>"
	exit 1
    fi

    build_fs $@
    exit 0
}

main $@
exit 0
