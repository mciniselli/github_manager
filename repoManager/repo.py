import os
from utils.github_helper import GithubHelper

from repoManager.file import File

class Repo:
    def __init__(self, repository_name: str, repository_url: str, commit: str ):
        self.repository_name=repository_name
        self.repository_url=repository_url
        self.commit = commit
        self.is_repo_ok=True
        self.files=list()

    def clone_repo(self, base_path: str):
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
        # self.cloned_directory="cloning_folder/packages_apps_Trebuchet"

        print("REPO OK {}".format(self.is_repo_ok))

        if not self.is_repo_ok:
            return

        files= self.get_list_of_files(self.cloned_directory)
        java_files=[os.path.join(os.getcwd(), f) for f in files if f.endswith(".java")]
        files=list()
        for f in java_files[:3]:
            file=File(f)
            files.append(file)

        self.files=files

        for f in self.files:
            f.add_methods()

        # print(self.files[0].filename)
        # self.files[0].add_methods()


    def get_list_of_files(self, dir_name: str):
        # create a list of file and sub directories
        # names in the given directory
        list_of_file = os.listdir(dir_name)
        all_files = list()
        # Iterate over all the entries
        for entry in list_of_file:
            # Create full path
            full_path = os.path.join(dir_name, entry)
            # If entry is a directory then get the list of files in this directory
            if os.path.isdir(full_path):
                all_files = all_files + self.get_list_of_files(full_path)
            else:
                all_files.append(full_path)

        return all_files