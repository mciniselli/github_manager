
from repoManager.repo import Repo
from repoManager.condition import Condition
from repoManager.method import Method

from srcML.srcml_filters import SrcmlFilters
import os
import shutil
from utils.logger import Logger
import copy
import utils.settings as settings
import codecs

from typing import List

class FileManager:
    def __init__(self, file_path: str):
        self.file=None
        self.file_path=file_path
        self.log = settings.logger

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

        self.log = settings.logger

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

    def export_condition_with_data(self, method: Method, condition: Condition, data: List[str]):

        new_condition = SrcmlFilters("<expr>&lt;x&gt;</expr>", True)

        xml=copy.copy(condition.condition)

        # xml=condition.condition
        condition_start=condition.start
        condition_end=condition.end

        expression=xml.select_one("expr")

        xml.select_one("expr").replaceWith(new_condition.xml_code)

        xml_method=copy.copy(method.xml)

        xml_method.find("if", {"pos:end": condition_end, "pos:start": condition_start}).replaceWith(xml)

        # self.log.info("__________")
        # self.log.info("METHOD")
        # self.log.info(xml_method.text)
        # self.log.info("MASK")
        # self.log.info(expression.text)
        # self.log.info("__________")

        self.file_masked.write_file(xml_method.text.replace("\n", " "))
        self.file_mask.write_file(expression.text.replace("\n", " "))
        self.info.write_file(str(data))


    def export_data(self, repo: Repo):

        self.file_mask=FileManager("mask.txt")
        self.file_masked=FileManager("masked.txt")
        self.info=FileManager("info.txt")

        self.file_mask.open_file("a+")
        self.file_masked.open_file("a+")
        self.info.open_file("a+")

        export_dir=os.path.join("export", repo.repository_name+"_"+repo.commit)

        if os.path.exists(export_dir):
            shutil.rmtree(export_dir)

        os.makedirs(export_dir)

        condition_ok=FileManager("condition_ok.txt")
        condition_ok.open_file("a+")
        condition_ko=FileManager("condition_ko.txt")
        condition_ko.open_file("a+")
        repo_status=FileManager("repo_status.txt")
        repo_status.open_file("a+")

        info_repo=list()
        info_repo.append(repo.repository_name)
        info_repo.append(repo.repository_url)
        info_repo.append(repo.commit)

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

        repo_status.write_file("{} {} {} {} {} {}".format(repo.repository_name, repo.repository_url, repo.is_repo_ok, repo.message_clone, repo.version, repo.is_tag))
        repo_status.close_file()

        f = FileManager(os.path.join(export_dir, "list_of_files.txt"))
        f.open_file("w+")
        for file in repo.files:
            f.write_file(file.filename)
            info_file=list()
            info_file.append(file.filename)

            filename=file.filename.split("/")[-1]
            file_without_extension=".".join(filename.split(".")[:-1])
            file_dir=os.path.join(export_dir, file_without_extension)
            # if we have the same file name in a different path
            if os.path.exists(file_dir):
                base_file_dir=file_dir+"_"
                i=0
                while os.path.exists(base_file_dir+str(i)):
                    i+=1
                file_dir=base_file_dir+str(i)
            os.makedirs(file_dir, exist_ok=True)

            info_file.append(file_dir)

            shutil.copy(file.filename, os.path.join(file_dir, filename))
            shutil.copy(file.filename.replace(".java", ".xml"), os.path.join(file_dir, filename).replace(".java", ".xml"))
            for i, method in enumerate(file.methods):
                m=FileManager(os.path.join(file_dir, "METHOD_{}.txt".format(i)))

                info_method=list()
                info_method.append("METHOD_{}.txt".format(i))
                info_method.append(method.start)
                info_method.append(method.end)

                m.open_file("w+")
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

                    if condition.is_ok:
                        condition_ok.write_file(condition.text)
                        condition_ok.write_file("__________")
                        info_condition=list()
                        info_condition.extend(info_repo)
                        info_condition.extend(info_file)
                        info_condition.extend(info_method)
                        info_condition.append(condition.start)
                        info_condition.append(condition.end)
                        info_condition.append(condition.type)
                        self.export_condition_with_data(method, condition, info_condition)
                    else:
                        condition_ko.write_file(condition.text)
                        condition_ko.write_file("__________")

                m.close_file()


        f.close_file()

        condition_ok.close_file()
        condition_ko.close_file()

        self.file_mask.close_file()
        self.file_masked.close_file()
        self.info.close_file()




    def create_file_masked(self, repo: Repo):

        self.file_mask=FileManager("mask.txt")
        self.file_masked=FileManager("masked.txt")
        self.info=FileManager("info.txt")

        self.file_mask.open_file("a+")
        self.file_masked.open_file("a+")
        self.info.open_file("a+")

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
        self.info.close_file()

        # file_log.close_file()
