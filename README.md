# Zotero Remarkable2 Sync

Using code from https://github.com/oscarmorrison/zoteroRemarkable, but I use a more up to date version of Zotero and the ReMarkable2.
It should be noted that this script currently does not sync the whole Zotero library, just a collection in "My Library" (recursively).
Currently this code is also just a one way sync, the collection in "My Library" will dictate what appears on the ReMarkable2.

My Zotero version is 5.0.96.2, my ReMarkable2 version is 2.7.0.51.
# **Disclaimer**
Use this software at your own risk!
The files are offered without any warranty and you will be violating the reMarkable AS EULA by using them. There may be bugs, you may lose data, your device may crash, etc.

## Setup
On the computer that has Zotero installed on it
 - install [rmapi](https://github.com/juruen/rmapi)
- 'pip install -r requirements.txt'
 - Download the [sync.py](https://github.com/Jbwasse2/ZoteroReMarkable2/blob/master/sync.py)
- Create a folder on the ReMarkable2 and a collection in zotero under "My Library" to transfer files between.
 - `mv example.env my.env`
 - Fill in details of my.env (see Env file section)


### Env file
- Follow the QuickStart section of https://github.com/urschrei/pyzotero which does a good job of explaining how to get the following
  - (API_KEY) Zotero api_key
  - (LIBRARY_ID) Zotero library_id
  - Currently library_type is set to just 'user', 'group' has not been tested yet. Don't worry about this if your collection is in "My Library". I have not tested syncing between a Group Library yet, but you can try editing "LIBRARY_TYPE = 'user'" to "LIBRARY_TYPE = 'group'" and see what happens.
- COLLECTION_NAME is the name of the collection in 'My Library' that you wish to sync with the ReMarkable2.
- FOLDER_NAME is the directory to the created folder on the ReMarkable2. So if for example you have a file system where you want to sync a folder named "zotero" and it is in a folder called "research" which sits on the top level of your file system, "FOLDER_NAME=/research/zotero"
- STORAGE_BASE_PATH can be found by going into zotero then pressing edit in the tool bar -> preferences -> advanced and under the "Files and Folders" tab there is a selection for "Data Directory Location" which shows where your files are being stored. Take this path and add "storage" to it, so if your directory is shown to be "/home/user/Zotero/" then "STORAGE_BASE_PATH=/home/user/Zotero/storage".

### Usage
_(ensure you have a .env file, with zotero api key, and rmapi setup)_
Then to sync, just run:
  `python3 sync.py`
