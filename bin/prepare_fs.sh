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

function newdir() {
    dirname=$1
    if [[ -d $dirname ]]; then
	sudo rm -rf $dirname
    fi
    mkdir -p $dirname
}

function manjaro() {
    expect "uname -a | grep -i manjaro" "Manjaro is not the current platform"
    expect "pacman -Qs manjaro-tools-base" "Missing package: manjaro-tools-base"

    rootfs=$1
    if [[ $rootfs == "" ]]; then
	rootfs=tmp
    fi

    newdir $rootfs
    sudo basestrap -cdGM $rootfs filesystem pacman pacaur

    sudo sh -c "cat $rootfs/etc/pacman.d/mirrorlist | grep -i -A2 --no-group-separator United_States > $rootfs/etc/pacman.d/mirrorlist"

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
