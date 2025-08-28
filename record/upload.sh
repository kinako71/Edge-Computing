#!/bin/bash

ftp_string=$1
data_dir=$2

if pgrep -x lftp > /dev/null; then
    echo "lftp is already running. Exiting."
    exit 1
fi

lftp -c "
set ftp:list-options -a;
set ssl-force on;
set passive-mode on;
set ssl:verify-certificate no;
set net:timeout 300;
set net:max-retries 3;
set net:reconnect-interval-base 5;
set net:reconnect-interval-multiplier 2;
set sftp:connect-program 'ssh -a -x -o StrictHostKeyChecking=no';
open sftp://sftp_user:sftp_user@100.115.135.20;
mirror --reverse --Remove-source-files --only-missing --verbose data uploaded_files;
" 