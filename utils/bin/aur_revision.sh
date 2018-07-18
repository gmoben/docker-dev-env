# -*- mode: shell-script -*-
# /bin/env bash

function usage() {
    echo "Installs a specific revision of an AUR package manually"
    echo
    echo "Usage: aur_revision [package_name] [revision] [user]"
    echo "Example: Download and install revision 1.10."
}

function aur_revision() {
    PKG_NAME=$1
    REVISION=$2
    LOCAL_USER=$3
    REPO_URL=https://aur.archlinux.org/$PKG_NAME.git
    PACAUR_DIR=/home/$LOCAL_USER/.cache/pacaur
    REPO_DIR=$PACAUR_DIR/$PKG_NAME

    mkdir -p $PACAUR_DIR
    git clone $AUR_REPO
    chmod a+rwx $AUR_REPO
    chown -R $LOCAL_USER:$LOCAL_USER $PACAUR_DIR
    cd $PKG_NAME
    git reset --hard $REVISION
    sudo -u $LOCAL_USER makepkg
    ls $PKG_NAME-*.pkg.tar.xz | xargs pacman -U --noconfirm
}

if [[ $@ == *"--help"* ]] || [[ $@ == *"-h" ]] ; then
    usage
    exit 0
fi

if [[ $1 == "" ]] || [[ $2 == "" ]] || [[ $3 == "" ]] ; then
    usage
    exit 1
fi

aur_revision $@
