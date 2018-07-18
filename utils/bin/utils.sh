#/bin/env bash

function expect() {
    cmd=$1
    failure_msg=$2
    return_code=$3

    if [[ `echo $return_code` == "" ]]; then
	return_code=0
    fi

    `eval $cmd &> /dev/null`
    if [[ $? -ne $return_code ]]; then
	echo $failure_msg
	exit 1
    fi
}

function expect_package() {
    expect "pacman -Qs $1" "Missing package: $1"
}

function expect_manjaro() {
    expect "uname -a | grep -i manjaro" "Manjaro is not the current platform"
    expect_package manjaro-release
    expect_package manjaro-tools-base
}

function get_package_version() {
    echo `pacman -Qs $1 | head -n 1 | awk '{print $2;}'`
}

function newdir() {
    dirname=$1
    if [[ -d $dirname ]]; then
	sudo rm -rf $dirname
    fi
    mkdir -p $dirname
}
