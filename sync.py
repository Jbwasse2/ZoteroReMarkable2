import os
import pickle
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from pydash import _
from pyzotero import zotero as pyzotero


#Zotero gets mad if you try to use pyzotero too much which is a pain for development.
#So this is a nice tool to save the collection structure reported by zotero.
def saveCollection(l):
    fp = open('testZotero.pkl', 'wb')
    pickle.dump(l, fp)


# Software practices are like a good analogy. I don't have one.
class GodClass():
    def __init__(self, debug, limit=200):
        self.debug = debug
        self.API_KEY, self.LIBRARY_ID, self.COLLECTION_NAME, self.FOLDER_NAME, self.STORAGE_BASE_PATH, self.LIBRARY_TYPE = self.get_env_vars()
        self.zotero = pyzotero.Zotero(self.LIBRARY_ID, self.LIBRARY_TYPE, self.API_KEY)
        self.collections = self.zotero.collections(limit=limit)
        self.parent_collection_id = self.getCollectionId(self.COLLECTION_NAME, self.collections)
        self.sub_collection = self.get_sub_collection(self.parent_collection_id, self.FOLDER_NAME)
        self.setup_file_structure(self.sub_collection)

    def setup_file_structure(self, sub_collection):
        for (_,folder) in sub_collection:
            flag = 0
            command = "rmapi find " + folder
            try:
                results = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode("utf-8").split('\n')
            except subprocess.CalledProcessError as e:
                if "directory doesn't exist" in str(e.output):
                    flag = 1
            expected_results = "[d] " + os.path.basename(folder)
            #Don't have to worry about ordering of creating dir
            #because of recursion in get_sub_collection
            if expected_results not in results or flag:
                command = "rmapi mkdir " + folder
                results = subprocess.check_output(command, shell=True).decode("utf-8")

    # oh boy intro to programming recursion here I come
    # my gut feeling is that this might slow stuff down because
    # the computational complexity might be huge.
    def get_sub_collection(self, parent_node_id, parent_dir):
        #WoNt SoMeBoDy ThInK oF tHe ChIlDrEn
        children = []
        for collection in self.collections:
            parent = collection.get('data').get('parentCollection')
            if parent == parent_node_id:
                children.append((collection.get('data').get('key'),collection.get('data').get('name') ))
        ret = [(parent_node_id, parent_dir)]
        for child in children:
            ret = ret + self.get_sub_collection(child[0], parent_dir + "/" +  child[1])
        return ret

    def get_env_vars(self):
        script_dir = sys.path[0]
        path = Path(script_dir + "/my.env")
        load_dotenv(dotenv_path=path)


        LIBRARY_TYPE = 'user'
        # user config variables. set these in a .env
        API_KEY = os.getenv('API_KEY')
        LIBRARY_ID = os.getenv('LIBRARY_ID')
        COLLECTION_NAME = os.getenv('COLLECTION_NAME') #in Zotero
        FOLDER_NAME = os.getenv('FOLDER_NAME') #on the Remarkable device, this must exist!
        STORAGE_BASE_PATH = os.getenv('STORAGE_BASE_PATH') #on local computer
        return API_KEY, LIBRARY_ID, COLLECTION_NAME, FOLDER_NAME, STORAGE_BASE_PATH, LIBRARY_TYPE

    def getCollectionId(self, collection_name, collections):
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

    def getPapersFromRemarkable(self, folder_name):
        RMAPI_LS = f"rmapi ls {folder_name}"
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

    def uploadPapers(self, papers, cloud_path):
        print(f'uploading {len(papers)} papers')
        for paper in papers:
            path = paper.get('path')
            COMMAND = f"rmapi put \"{path}\" {cloud_path}"
            try:
                print(COMMAND)
                os.system(COMMAND)
            except Exception as e:
                print(f'Failed to upload {path}')
                print(e)

    def getDeleteListOfPapers(self, remarkable_files, papers):
        delete_list = []
        paperNames = []
        for paper in papers:
            paperNames.append(os.path.splitext(paper.get('title'))[0])
        for f in remarkable_files:
            if (f not in paperNames):
                delete_list.append(f)
        return delete_list

    def deletePapers(self, delete_list, cloud_path):
        print(f'deleting {len(delete_list)} papers')
        for paper in delete_list:
            COMMAND = f"rmapi rm {cloud_path}/\"{paper}\""
            try:
                print(COMMAND)
                os.system(COMMAND)
            except:
                print(f'Failed to delete {paper}')

    def synchronize(self):
        # get papers that we want from Zetero Remarkable collection
        for collection in self.sub_collection :
            collection_id, cloud_path = collection
            papers = self.getPapersTitleAndPathsFromZoteroCollection(self.zotero, collection_id, self.STORAGE_BASE_PATH)
            print(f"{len(papers)} papers in Zotero {self.COLLECTION_NAME} collection name")
            for paper in papers:
                print(paper.get('title'))

            #get papers that are currently on remarkable
            remarkable_files = self.getPapersFromRemarkable(cloud_path)
            print(f"{len(remarkable_files)} papers on Remarkable Device, {cloud_path}")

            upload_list = self.getUploadListOfPapers(remarkable_files, papers)
            self.uploadPapers(upload_list, cloud_path)

            #Still need to test this a bit
            delete_list = self.getDeleteListOfPapers(remarkable_files, papers)
            self.deletePapers(delete_list, cloud_path)

if __name__ == "__main__":
    print('------- sync started -------')
    synchronizer = GodClass(debug=False)
    synchronizer.synchronize()
    print('------- sync complete -------')
