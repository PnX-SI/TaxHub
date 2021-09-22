#!/bin/bash

BASEDIR=$(dirname "$0")


create_sys_dir() {
    dirs=("${BASEDIR}/tmp/" "${BASEDIR}/var/log/" "${BASEDIR}/var/log/installdb/")
    for i in ${dirs[@]}
    do
        if [ ! -d $i ]
        then
            parentdir="$(dirname "$i")"
            mkdir -p $i
        fi
    done
    
    echo "Répertoires système créés"
}
