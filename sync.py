import os
import pickle
import subprocess
from pathlib import Path

import pudb
from dotenv import load_dotenv
from pydash import _
from pyzotero import zotero as pyzotero


#Zotero gets mad if you try to use pyzotero too much which is a pain for development.
#So this is a nice tool to save the collection structure reported by zotero.
def saveCollection(l):
    fp = open('testZotero.pkl', 'wb')
    pickle.dump(l, fp)


class GodClass():
    def __init__(self, debug):
        self.debug = debug
        self.API_KEY, self.LIBRARY_ID, self.COLLECTION_NAME, self.FOLDER_NAME, self.STORAGE_BASE_PATH, self.LIBRARY_TYPE = self.get_env_vars()
        self.RMAPI_LS = f"rmapi ls /{self.FOLDER_NAME}"
        self.zotero = pyzotero.Zotero(self.LIBRARY_ID, self.LIBRARY_TYPE, self.API_KEY)
        self.parent_collection = None


    def get_env_vars(self):
        path = Path("./my.env")
        load_dotenv(dotenv_path=path)


        LIBRARY_TYPE = 'user'
        # user config variables. set these in a .env
        API_KEY = os.getenv('API_KEY')
        LIBRARY_ID = os.getenv('LIBRARY_ID')
        COLLECTION_NAME = os.getenv('COLLECTION_NAME') #in Zotero
        FOLDER_NAME = os.getenv('FOLDER_NAME') #on the Remarkable device, this must exist!
        STORAGE_BASE_PATH = os.getenv('STORAGE_BASE_PATH') #on local computer
        return API_KEY, LIBRARY_ID, COLLECTION_NAME, FOLDER_NAME, STORAGE_BASE_PATH, LIBRARY_TYPE

    def getCollectionId(self, zotero, collection_name):
        collections = zotero.collections(limit=200)
        for collection in collections:
            if (collection.get('data').get('name') in collection_name):
                return collection.get('data').get('key')

    def getPapersTitleAndPathsFromZoteroCollection(self, zotero, collection_id, STORAGE_BASE_PATH, collection_items=None):
        papers = []
        if collection_items == None:
            collection_items = zotero.collection_items(collection_id);
        for item in collection_items:
            content_type = item.get('data').get('contentType')
            if( content_type == 'application/pdf'): 
                item_pdf_path = STORAGE_BASE_PATH + item.get('data').get('key')
                item_title = item.get('data').get('filename')
                if (item_pdf_path and item_title):
                    papers.append({ 'title': item_title, 'path': item_pdf_path + "/" + item_title })
        return papers

    def getPapersFromRemarkable(self, RMAPI_LS):
        remarkable_files = []
        for f in subprocess.check_output(RMAPI_LS, shell=True).decode("utf-8").split('\n'):
            if '[d]\t' not in f and f != "":
                remarkable_files.append(f.strip('[f]\t'))
        return remarkable_files

    def getUploadListOfPapers(self, remarkable_files, papers):
        upload_list = []
        for paper in papers:
            title = os.path.splitext(paper.get('title'))[0]
            if title not in remarkable_files:
                upload_list.append(paper)
        return upload_list

    def uploadPapers(self, papers):
        print(f'uploading {len(papers)} papers')
        for paper in papers:
            path = paper.get('path')
            COMMAND = f"rmapi put \"{path}\" /{self.FOLDER_NAME}"
            try:
                print(COMMAND)
                os.system(COMMAND)
            except:
                print(f'Failed to upload {path}')

    def getDeleteListOfPapers(self, remarkable_files, papers):
        delete_list = []
        paperNames = []
        for paper in papers:
            paperNames.append(os.path.splitext(paper.get('title'))[0])
        pu.db
        for f in remarkable_files:
            if (f not in paperNames):
                delete_list.append(f)
        return delete_list

    def deletePapers(self, delete_list):
        print(f'deleting {len(delete_list)} papers')
        for paper in delete_list:
            COMMAND = f"rmapi rm /{FOLDER_NAME}/\"{paper}\""
            try:
                print(COMMAND)
                os.system(COMMAND)
            except:
                print(f'Failed to delete {paper}')

    def synchronize(self):
        if self.debug:
            fp = open("./testZotero.pkl", "rb")
            collection_items = pickle.load(fp)
            collection_id = None
            papers = self.getPapersTitleAndPathsFromZoteroCollection(self.zotero, collection_id, self.STORAGE_BASE_PATH, collection_items)
        else:
            collection_id = self.getCollectionId(self.zotero, self.COLLECTION_NAME)

            # get papers that we want from Zetero Remarkable collection
            papers = self.getPapersTitleAndPathsFromZoteroCollection(self.zotero, collection_id, self.STORAGE_BASE_PATH)
        print(f"{len(papers)} papers in Zotero {self.COLLECTION_NAME} collection name")
        for paper in papers:
            print(paper.get('title'))

        #get papers that are currently on remarkable
        remarkable_files = self.getPapersFromRemarkable(self.RMAPI_LS)
        print(f"{len(remarkable_files)} papers on Remarkable Device, /{self.FOLDER_NAME}")

        upload_list = self.getUploadListOfPapers(remarkable_files, papers)
        self.uploadPapers(upload_list)

        delete_list = self.getDeleteListOfPapers(remarkable_files, papers)
        self.deletePapers(delete_list)

if __name__ == "__main__":
    print('------- sync started -------')
    synchronizer = GodClass(debug=True)
    synchronizer.synchronize()
    print('------- sync complete -------')
