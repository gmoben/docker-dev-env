#/bin/env bash

readonly BIN_DIR=$(cd "$(dirname "$0")" > /dev/null && pwd -P)
source $BIN_DIR/utils.sh

expect_manjaro

if [[ $@ != *"--skip-upgrade" ]]; then
    read -n 1 -p "Want to attempt a full upgrade before continuing? (y/n) " yn
    echo
    case $yn in
        y|Y) sudo pacman -Syuu --noconfim ;;
    	*)   echo "Skipping upgrade" ;;
    esac
fi

version=`get_package_version manjaro-release`

echo "Using manjaro $version"
