#!/bin/bash

# check if the user is root
if [ $(id -u) != "0" ]; then
    echo "Error: You must be root to run this script"
    exit 1
fi

# remove from /usr/bin
rm -f /usr/bin/bmpv

# remove from mimeapps.list
sed -i '/bmpv/d' ~/.config/mimeapps.list

# remove from /usr/share/applications
rm -f /usr/share/applications/bmpv.desktop

# echo success
echo "bmpv has been uninstalled successfully"

# remind user to remove script from tampermonkey
echo "Please remove the script from tampermonkey manually"
