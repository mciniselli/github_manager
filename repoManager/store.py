
from repoManager.repo import Repo
from repoManager.condition import Condition
from repoManager.method import Method

from srcML.srcml_filters import SrcmlFilters
import os
import shutil
from utils.logger import Logger
import copy

import codecs

class FileManager:
    def __init__(self, file_path: str):
        self.file=None
        self.file_path=file_path
        self.log_class = Logger()
        self.log = self.log_class.log

    def open_file(self, mode: str):
        self.file=codecs.open(self.file_path, mode=mode, encoding="utf-8" )

    def close_file(self):
        self.file.close()

    def read_file(self):
        try:
            self.open_file(self.file_path, "r")

            content = self.file.readlines()
            c_ = list()
            for c in content:
                r = c.rstrip("\n").rstrip("\r")
                c_.append(r)

        except Exception as e:
            self.log.error("Error ReadFile: " + str(e))
            c_ = []
        finally:
            self.close_file()
        return c_

    def write_file(self, element):  # write generic file

        self.file.write(element + "\n")

class Store:
    def __init__(self):

        self.log_class = Logger()
        self.log = self.log_class.log

    def export_condition(self, method: Method, condition: Condition):

        new_condition = SrcmlFilters("<expr>&lt;x&gt;</expr>", True)

        xml=copy.copy(condition.condition)

        # xml=condition.condition
        condition_start=condition.start
        condition_end=condition.end

        expression=xml.select_one("expr")

        xml.select_one("expr").replaceWith(new_condition.xml_code)

        xml_method=copy.copy(method.xml)

        xml_method.find("if", {"pos:end": condition_end, "pos:start": condition_start}).replaceWith(xml)

        self.log.info("__________")
        self.log.info("METHOD")
        self.log.info(xml_method.text)
        self.log.info("MASK")
        self.log.info(expression.text)
        self.log.info("__________")

        self.file_masked.write_file(xml_method.text.replace("\n", " "))
        self.file_mask.write_file(expression.text.replace("\n", " "))


    def export_data(self, repo: Repo):

        export_dir=os.path.join("export", repo.repository_name+"_"+repo.commit)

        if os.path.exists(export_dir):
            shutil.rmtree(export_dir)

        os.makedirs(export_dir)


        f=FileManager(os.path.join(export_dir, "repo_info.txt"))
        f.open_file("w+")
        f.write_file("NAME: {}".format(repo.repository_name))
        f.write_file("URL: {}".format(repo.repository_url))
        f.write_file("COMMIT: {}".format(repo.commit))
        f.write_file("IS REPO OK: {}".format(repo.is_repo_ok))
        f.write_file("MESSAGE CLONE: {}".format(repo.message_clone))
        if repo.cloned_directory is not None:
            f.write_file("CLONED DIRECTORY: {}".format(repo.cloned_directory))
        f.write_file("VERSION: {}".format(repo.version))
        f.write_file("IS_TAG: {}".format(repo.is_tag))
        f.close_file()

        f = FileManager(os.path.join(export_dir, "list_of_files.txt"))
        f.open_file("w+")
        for file in repo.files:
            f.write_file(file.filename)
            filename=file.filename.split("/")[-1]
            file_without_extension=".".join(filename.split(".")[:-1])
            file_dir=os.path.join(export_dir, file_without_extension)
            os.makedirs(file_dir)
            shutil.copy(file.filename, os.path.join(file_dir, filename))
            shutil.copy(file.filename.replace(".java", ".xml"), os.path.join(file_dir, filename).replace(".java", ".xml"))
            for i, method in enumerate(file.methods):
                m=FileManager(os.path.join(file_dir, "METHOD_{}.txt".format(i)))
                m.open_file()
                m.write_file("METHOD START {}, END {}".format(method.start, method.end))
                m.write_file(method.raw_code)
                m.write_file("__________")
                m.write_file(method.text)
                num_ok=0
                for condition in method.conditions:
                    if condition.is_ok:
                        num_ok+=1
                m.write_file("CONDITIONS OK: {} OUT OF {}".format(num_ok, len(method.conditions)))

                for condition in method.conditions:
                    m.write_file("CONDITION START {}, END {}".format(condition.start, condition.end))
                    m.write_file("IS OK {}, TYPE {}".format(condition.is_ok, condition.type))
                    m.write_file(condition.raw_code)
                    m.write_file("__________")
                    m.write_file(condition.text)

                m.close_file()


        f.close_file()






    def create_file_masked(self, repo: Repo):

        self.file_mask=FileManager("mask.txt")
        self.file_masked=FileManager("masked.txt")

        self.file_mask.open_file("a+")
        self.file_masked.open_file("a+")

        # file_log=FileManager("global_info.txt")
        # file_log.open_file("a+")

        for file in repo.files:
            for method in file.methods:
                for condition in method.conditions:
                    if condition.is_ok:
                        self.export_condition(method, condition)

        self.export_data(repo)

        # file_log.write_file("______REPO_______")
        # file_log.write_file("Repo {} {}: {}".format(repo.base_path, repo.repository_name, repo.is_repo_ok))
        # file_log.write_file("NUM FILES: {}".format(len(repo.files)))
        #
        # for file in repo.files:
        #     file_log.write_file("_____FILE________")
        #     file_log.write_file("{}: {} methods".format(file.filename, len(file.methods)))
        #     for method in file.methods:
        #         file_log.write_file("_____METHOD________")
        #         file_log.write_file("{}".format(method.raw_code))
        #         file_log.write_file("NUM CONDITIONS: {}".format(len(method.conditions)))
        #         for condition in method.conditions:
        #             file_log.write_file("_____CONDITION________")
        #             file_log.write_file("{}-{}: {}".format(condition.is_ok, condition.type, condition.condition.text.replace("\n", " ")))


        self.file_mask.close_file()
        self.file_masked.close_file()

        # file_log.close_file()
