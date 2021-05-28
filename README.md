# Zotero Remarkable2 Sync
##Disclaimer
Use this software at your own risk!
The files are offered without any warranty and you will be violating the reMarkable AS EULA by using them. There may be bugs, you may lose data, your device may crash, etc.

Using code from https://github.com/oscarmorrison/zoteroRemarkable, but I use a more up to date version of Zotero and the ReMarkable2.
It should be noted that this script currently does not sync the whole Zotero library, just a collection in "My Library".
Currently this code is also just a one way sync, the collection in "My Library" will dictate what appears on the ReMarkable2.

My Zotero version is 5.0.96.2, my ReMarkable2 version is 2.7.0.51.

## Setup
 - install rmapi
 - Download the [sync.py](https://github.com/Jbwasse2/ZoteroReMarkable2/blob/master/sync.py)
 - `mv example.env my.env`

### Dependancies
- python3
- [rmapi](https://github.com/juruen/rmapi)
- 'pip install -r requirements.txt' to install other python packages through pip


### Env file
- Visit https://github.com/urschrei/pyzotero and get the following
  - Create a zotero api key
  - get zotero library_id (from zotero web)
  - Currently library_type is set to just 'user', 'group' has not been tested yet.
- COLLECTION_NAME is the name of the collection in 'My Library' that you wish to sync with the
- create a folder on remarkable and a collection in zotero
- get base path for zotero pdf (papers)

### Usage
_(ensure you have a .env file, with zotero api key, and rmapi setup)_
Then to sync, just run:
  `python3 sync.py`
