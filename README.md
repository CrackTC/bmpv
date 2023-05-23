# bmpv
> :wrench: this is WIP, configuration support will be added soon

a simple tool for playing bilibili video in [mpv](https://mpv.io/)
based on [BBDown](https://github.com/nilaoda/BBDown)
and [danmaku2ass](https://github.com/m13253/danmaku2ass)

## Features
- play bilibili video in mpv when opening a video page in browser
- danmaku support (with danmaku2ass)
- Dolby Vision support

## Dependencies
- mpv
- BBDown
- danmaku2ass
- python3
- tampermonkey

## Installation
1. Clone this repo and run install.sh, note that you need to have root permission to install

   this will install the bmpv.py to /usr/bin/bmpv,
   adding a .desktop file to /usr/share/applications
   and add a mime type for `bmpv://` protocol

   ```bash
   git clone https://github.com/CrackTC/bmpv.git
   cd bmpv
   sudo ./install.sh
   ```
1. Add `bmpv.user.js` to tampermonkey manually

## Uninstallation
1. Run uninstall.sh with root permission

   ```bash
   sudo ./uninstall.sh
   ```

1. Don't forget to remove `bmpv.user.js` from tampermonkey~

## Configuration
WIP

## License
MIT
