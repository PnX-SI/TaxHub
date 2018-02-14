#!/bin/bash

create_sys_dir() {
    dirs=('/tmp/taxhub/' '/tmp/usershub/' '/var/log/taxhub/' '/var/log/taxhub/installdb/')
    for i in ${dirs[@]}
    do
        if [ ! -d $i ]
        then
            parentdir="$(dirname "$i")"
            if [ -w $parentdir ] ; 
            then 
                mkdir -p $i
            else 
                sudo mkdir -p $i
                sudo chown -R "$(id -u)" $i
            fi
            chmod -R 775 $i
        fi
    done
    
    echo "Répertoires système créés"
}
