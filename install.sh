#!/bin/bash

# cd to the directory of this script
cd "$(dirname "$0")"

# check if the user is root
if [ $(id -u) != "0" ]; then
    echo "Error: You must be root to run this script"
    exit 1
fi

# check if bmpv is installed
if [ -f /usr/bin/bmpv ]; then
    echo "Error: bmpv is already installed at /usr/bin/bmpv"
    exit 1
fi

# check dependencies

# mpv
if ! command -v mpv >/dev/null 2>&1; then
    echo "Error: mpv is not installed"
    exit 1
fi

# python3
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 is not installed"
    exit 1
fi

# requests
if ! python3 -c "import requests" >/dev/null 2>&1; then
    echo "Error: [python]requests is not installed"
    exit 1
fi

# urllib
if ! python3 -c "import urllib" >/dev/null 2>&1; then
    echo "Error: [python]urllib is not installed"
    exit 1
fi

# BBDown
if ! command -v BBDown >/dev/null 2>&1; then
    echo "Error: BBDown is not installed"
    exit 1
fi

# danmaku2ass
if ! command -v danmaku2ass >/dev/null 2>&1; then
    echo "Error: danmaku2ass is not installed"
    exit 1
fi

# copy desktop entry
cp ./bmpv.desktop /usr/share/applications/

# insert to [Added Associations] in mimeapps.list
sed -i '/\[Added Associations\]/a x-scheme-handler/bmpv=bmpv.desktop' ~/.config/mimeapps.list

# copy bmpv.py to /usr/bin
cp ./bmpv.py /usr/bin/bmpv

# make it executable
chmod +x /usr/bin/bmpv

# echo success
echo "bmpv installed successfully"

# remind user to add script to tampermonkey
echo "Please add biliplay.user.js to tampermonkey"

# print biliplay.user.js
cat ./biliplay.user.js
