import os
from utils.github_helper import GithubHelper

from repoManager.file import File

class Repo:
    def __init__(self, repository_name, repository_url, commit ):
        self.repository_name=repository_name
        self.repository_url=repository_url
        self.commit = commit
        self.is_repo_ok=True
        self.files=None

    def clone_repo(self, base_path):
        self.base_path=base_path
        g = GithubHelper()
        result = g.clone(self.repository_name, self.base_path)

        if result == False:
            self.is_repo_ok=False

        folders=os.listdir(self.base_path)
        print(folders)
        self.cloned_directory = os.path.join(self.base_path, folders[0])

        result=g.checkout(self.cloned_directory)

        if result == False:
            self.is_repo_ok=False


    def add_files(self):

        # to be REMOVED
        self.cloned_directory="cloning_folder/packages_apps_Trebuchet"

        files=self.getListOfFiles(self.cloned_directory)
        java_files=[os.path.join(os.getcwd(), f) for f in files if f.endswith(".java")]
        files=list()
        for f in java_files:
            file=File(f)
            files.append(file)

        self.files=files

        print(self.files[0].filename)
        self.files[0].add_methods()


    def getListOfFiles(self, dirName):
        # create a list of file and sub directories
        # names in the given directory
        listOfFile = os.listdir(dirName)
        allFiles = list()
        # Iterate over all the entries
        for entry in listOfFile:
            # Create full path
            fullPath = os.path.join(dirName, entry)
            # If entry is a directory then get the list of files in this directory
            if os.path.isdir(fullPath):
                allFiles = allFiles + self.getListOfFiles(fullPath)
            else:
                allFiles.append(fullPath)

        return allFiles