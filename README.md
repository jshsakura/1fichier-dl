**Note:**
This a fork of the original project as it's no longer maintained.

# 1Fichier-dl
<p align="center">
  <b>1Fichier Download Manager</b>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/Leinad4Mind/1fichier-dl/main/Screenshot_Light.png"></img>
</p>

<p align="center">
  <b>Light mode</b>

<p align="center">
  <img src="https://raw.githubusercontent.com/Leinad4Mind/1fichier-dl/main/Screenshot_Dark.png"></img>
</p>

<p align="center">
  <b>Dark mode</b>

## Features
⭐ Manage your downloads

⭐ Bypass time limits

## Usage
- Make sure Python3 is installed properly, do `pip install -r requirements.txt` and then you can use `1fichier-dl.vbs` to launch the program

## Credits
* All icons, including the app icon, were provided by [Feather](https://feathericons.com/).
* Proxies provided by [Proxyscan](https://www.proxyscan.io/).
* Original author manuGMG

## Changes made so far 
 - GUI icons (and their scale)
 - Fix looping bug when proxy works but download fails
 - Allows to input custom proxy list via a URL in the Settings > Connection menu (example list: https://pastebin.com/raw/uVVLrxyd), should use HTTPS proxies, if you don't input anything then it defaults to getting proxies from proxyscan.io
  
## To do
  - Figure out a way to build this into a executable for release, haven't been succesful at it... for now use the VBS script