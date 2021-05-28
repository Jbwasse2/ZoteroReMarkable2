# Zotero Remarkable Sync
Using code from https://github.com/oscarmorrison/zoteroRemarkable, but I use a more up to date version of Zotero and the ReMarkable2.

This is a little utility that I made to keep a collection/folder in sync with Zotero and Remarkable.
My zotero setup uses external storage (I store all attachments on OneDrive)

## Setup
 - install rmapi
 - Download the [sync.py](https://raw.githubusercontent.com/oscarmorrison/zoteroRemarkableO/master/sync.py)
 - create a `.env` file

### Dependancies
- python3
- [rmapi](https://github.com/juruen/rmapi)
(Install the following with `pip install -r requirements.txt`)
- pyzotero
- pydash
- dotenv

### Env file
- Create a zotero api key
- get zotero library_id (from zotero web)
- See https://github.com/urschrei/pyzotero for more information
- create a folder on remarkable and a collection in zotero
- get base path for zotero pdf (papers)

### Usage
_(ensure you have a .env file, with zotero api key, and rmapi setup)_
Then to sync, just run:
  `python3 sync.py`
