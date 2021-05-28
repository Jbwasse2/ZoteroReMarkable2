import os
import subprocess
from pathlib import Path

import pudb
from dotenv import load_dotenv
from pydash import _
from pyzotero import zotero as pyzotero

path = Path("./env.env")
load_dotenv(dotenv_path=path)

# import pprint
# pp = pprint.PrettyPrinter(indent=4)
# # usage pp.pprint

LIBRARY_TYPE = 'user'

# user config variables. set these in a .env
API_KEY = os.getenv('API_KEY')
LIBRARY_ID = os.getenv('LIBRARY_ID')
COLLECTION_NAME = os.getenv('COLLECTION_NAME') #in Zotero
FOLDER_NAME = os.getenv('FOLDER_NAME') #on the Remarkable device, this must exist!
STORAGE_BASE_PATH = os.getenv('STORAGE_BASE_PATH') #on local computer

RMAPI_LS = f"rmapi ls /{FOLDER_NAME}"

zotero = pyzotero.Zotero(LIBRARY_ID, LIBRARY_TYPE, API_KEY)

def getCollectionId(zotero, collection_name):
    collections = zotero.collections(limit=200)
    for collection in collections:
        if (collection.get('data').get('name') == collection_name):
            return collection.get('data').get('key')

def getPapersTitleAndPathsFromZoteroCollection(zotero, collection_id, STORAGE_BASE_PATH):
    papers = []
    collection_items = zotero.collection_items(collection_id);
    for item in collection_items:
        if(item.get('data').get('contentType') == 'application/pdf'): 
            item_pdf_path = STORAGE_BASE_PATH + item.get('data').get('key')
            item_title = item.get('data').get('title')
            if (item_pdf_path and item_title):
                papers.append({ 'title': item_title, 'path': item_pdf_path + "/" + item_title })
    return papers

def getPapersFromRemarkable(RMAPI_LS):
    remarkable_files = []
    for f in subprocess.check_output(RMAPI_LS, shell=True).decode("utf-8").split('\n'):
        if '[d]\t' not in f and f != "":
            remarkable_files.append(f.strip('[f]\t'))
    return remarkable_files

def getUploadListOfPapers(remarkable_files, papers):
    upload_list = []
    for paper in papers:
        title = paper.get('title')
        if title not in remarkable_files:
            upload_list.append(paper)
    return upload_list

def uploadPapers(papers):
    print(f'uploading {len(papers)} papers')
    for paper in papers:
        path = paper.get('path')
        COMMAND = f"rmapi put \"{path}\" /{FOLDER_NAME}"
        try:
            print(COMMAND)
            os.system(COMMAND)
        except:
            print(f'Failed to upload {path}')

def getDeleteListOfPapers(remarkable_files, papers):
    delete_list = []
    paperNames = _(papers).map(lambda p: p.get('title')).value()
    for f in remarkable_files:
        if (f not in paperNames):
            delete_list.append(f)
    return delete_list

def deletePapers(delete_list):
    print(f'deleting {len(delete_list)} papers')
    for paper in delete_list:
        COMMAND = f"rmapi rm /{FOLDER_NAME}/\"{paper}\""
        try:
            print(COMMAND)
            os.system(COMMAND)
        except:
            print(f'Failed to delete {paper}')

print('------- sync started -------')
collection_id = getCollectionId(zotero, COLLECTION_NAME)

# get papers that we want from Zetero Remarkable collection
papers = getPapersTitleAndPathsFromZoteroCollection(zotero, collection_id, STORAGE_BASE_PATH)
print(f"{len(papers)} papers in Zotero {COLLECTION_NAME} collection name")
for paper in papers:
    print(paper.get('title'))

#get papers that are currently on remarkable
remarkable_files = getPapersFromRemarkable(RMAPI_LS)
print(f"{len(remarkable_files)} papers on Remarkable Device, /{FOLDER_NAME}")

upload_list = getUploadListOfPapers(remarkable_files, papers)
uploadPapers(upload_list)

delete_list = getDeleteListOfPapers(remarkable_files, papers)
deletePapers(delete_list)

print('------- sync complete -------')
