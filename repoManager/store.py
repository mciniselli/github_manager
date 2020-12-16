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

import csv


class FileManager:
    def __init__(self, file_path: str):
        self.file = None
        self.writer = None
        self.fieldnames = None
        self.file_path = file_path
        self.log = settings.logger

    def open_file_csv(self, mode: str, fieldnames: List[str]):
        write_header=True
        if os.path.exists(self.file_path):
            write_header=False
        self.file = open(self.file_path, mode=mode, encoding="utf-8")
        self.fieldnames = fieldnames
        self.writer = csv.DictWriter(self.file, fieldnames=self.fieldnames)
        if write_header:
            self.writer.writeheader()

    def example(self):
        with open('employee_file2.csv', mode='w') as csv_file:
            fieldnames = ['emp_name', 'dept', 'birth_month']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'emp_name': 'John Smith', 'dept': 'Accounting', 'birth_month': 'November'})
            writer.writerow({'emp_name': 'Erica Meyers', 'dept': 'IT', 'birth_month': 'March'})

    def write_file_csv(self, element_list: List[str]):
        self.writer.writerow(element_list)

    def close_file(self):
        self.file.close()

    def open_file_txt(self, mode: str):
        self.file = codecs.open(self.file_path, mode=mode, encoding="utf-8")

    def read_file_txt(self):
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

    def write_file_txt(self, element):  # write generic file

        self.file.write(element + "\n")


class Store:
    def __init__(self):

        self.log = settings.logger

    def export_condition(self, method: Method, condition: Condition):

        new_condition = SrcmlFilters("<expr>&lt;x&gt;</expr>", True)

        xml = copy.copy(condition.condition)

        # xml=condition.condition
        condition_start = condition.start
        condition_end = condition.end

        expression = xml.select_one("expr")

        xml.select_one("expr").replaceWith(new_condition.xml_code)

        xml_method = copy.copy(method.xml)

        xml_method.find("if", {"pos:end": condition_end, "pos:start": condition_start}).replaceWith(xml)

        self.log.info("__________")
        self.log.info("METHOD")
        self.log.info(xml_method.text)
        self.log.info("MASK")
        self.log.info(expression.text)
        self.log.info("__________")

        self.file_masked.write_file_txt(xml_method.text.replace("\n", " "))
        self.file_mask.write_file_txt(expression.text.replace("\n", " "))

    def export_condition_with_data(self, method: Method, condition: Condition, data: List[str]):

        new_condition = SrcmlFilters("<expr>&lt;x&gt;</expr>", True)

        xml = copy.copy(condition.condition)

        # xml=condition.condition
        condition_start = condition.start
        condition_end = condition.end

        expression = xml.select_one("expr")

        xml.select_one("expr").replaceWith(new_condition.xml_code)

        xml_method = copy.copy(method.xml)

        xml_method.find("if", {"pos:end": condition_end, "pos:start": condition_start}).replaceWith(xml)

        # self.log.info("__________")
        # self.log.info("METHOD")
        # self.log.info(xml_method.text)
        # self.log.info("MASK")
        # self.log.info(expression.text)
        # self.log.info("__________")

        self.file_masked.write_file_txt(xml_method.text.replace("\n", " "))
        self.file_mask.write_file_txt(expression.text.replace("\n", " "))
        self.info.write_file_txt(str(data))

    def export_data(self, repo: Repo):

        export_dir = "export"
        repo_dir = os.path.join("export", str(repo.id))

        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir)

        os.makedirs(repo_dir)

        condition_ok = FileManager("condition_ok.txt")
        condition_ok.open_file_txt("a+")
        condition_ko = FileManager("condition_ko.txt")
        condition_ko.open_file_txt("a+")
        repo_status = FileManager("repo_status.txt")
        repo_status.open_file_txt("a+")

        f = FileManager(os.path.join(export_dir, "repo_info.csv"))
        fields_repo = ["ID", "NAME", "URL", "COMMIT", "IS_REPO_OK", "MESSAGE_CLONE", "VERSION", "TAG"]
        values_repo = [str(repo.id), repo.repository_name, repo.repository_url, repo.commit, str(repo.is_repo_ok),
                  str(repo.message_clone), repo.version, str(repo.is_tag)]

        f.open_file_csv("a+", fields_repo)

        dict_repo = dict()
        for x, y in zip(fields_repo, values_repo):
            dict_repo[x] = y

        f.write_file_csv(dict_repo)


        f.close_file()

        repo_status.write_file_txt(
            "{} {} {} {} {} {}".format(repo.repository_name, repo.repository_url, repo.is_repo_ok, repo.message_clone,
                                       repo.version, repo.is_tag))
        repo_status.close_file()

        f = FileManager(os.path.join(repo_dir, "file_info.csv"))
        fields_file = ["ID", "NAME", "NUMBER_METHODS"]

        f.open_file_csv("w+", fields_file)

        for file in repo.files:
            values_file=[str(file.id), file.filename, str(len(file.methods))]

            dict_file = dict()
            for x, y in zip(fields_file, values_file):
                dict_file[x] = y

            f.write_file_csv(dict_file)

            file_dir = os.path.join(repo_dir, str(file.id))
            os.makedirs(file_dir, exist_ok=True)

            shutil.copy(file.filename, os.path.join(file_dir, "source.java"))
            shutil.copy(file.filename.replace(".java", ".xml"),
                        os.path.join(file_dir, "source.xml"))

            m = FileManager(os.path.join(file_dir, "method_info.csv"))
            fields_method = ["ID", "START", "END", "NUM_CONDITION", "NUM_CONDITION_OK", "ABSTRACTION_REQUIRED", "ABSTRACTION_OK"]

            m.open_file_csv("w+", fields_method)

            for i, method in enumerate(file.methods):

                num_ok = 0
                for condition in method.conditions:
                    if condition.is_ok:
                        num_ok += 1

                values_method = [str(method.id), method.start, method.end, str(len(method.conditions)), str(num_ok), str(method.abstraction_required), str(method.abstraction_ok)]


                dict_method = dict()
                for x, y in zip(fields_method, values_method):
                    dict_method[x] = y

                m.write_file_csv(dict_method)

                method_dir=os.path.join(file_dir, str(method.id))
                os.makedirs(method_dir, exist_ok=True)
                write_file=FileManager(os.path.join(method_dir, "source.java"))
                write_file.open_file_txt("w+")
                write_file.write_file_txt(method.text)
                write_file.close_file()

                write_file=FileManager(os.path.join(method_dir, "source.xml"))
                write_file.open_file_txt("w+")
                write_file.write_file_txt(method.raw_code)
                write_file.close_file()

                if method.abstraction_required and method.abstraction_ok:
                    write_file = FileManager(os.path.join(method_dir, "abstract.java"))
                    write_file.open_file_txt("w+")
                    write_file.write_file_txt(method.abstract)
                    write_file.close_file()

                    write_file = FileManager(os.path.join(method_dir, "abstract.java.map"))
                    write_file.open_file_txt("w+")
                    write_file.write_file_txt(method.dict_abstract)
                    write_file.close_file()

                c = FileManager(os.path.join(method_dir, "condition_info.csv"))
                fields_condition = ["ID", "START", "END", "IS_OK", "TYPE"]

                c.open_file_csv("w+", fields_condition)

                for condition in method.conditions:

                    values_condition=[str(condition.is_ok), condition.start, condition.end, str(condition.is_ok), condition.type]

                    dict_condition = dict()
                    for x, y in zip(fields_condition, values_condition):
                        dict_condition[x] = y

                    c.write_file_csv(dict_condition)

                    condition_dir = os.path.join(method_dir, str(condition.id))
                    os.makedirs(condition_dir, exist_ok=True)
                    write_file = FileManager(os.path.join(condition_dir, "source.java"))
                    write_file.open_file_txt("w+")
                    write_file.write_file_txt(condition.text)
                    write_file.close_file()

                    write_file = FileManager(os.path.join(condition_dir, "source.xml"))
                    write_file.open_file_txt("w+")
                    write_file.write_file_txt(condition.raw_code)
                    write_file.close_file()

                    if condition.is_ok:
                        condition_ok.write_file_txt(condition.text)
                        condition_ok.write_file_txt("__________")

                    else:
                        condition_ko.write_file_txt(condition.text)
                        condition_ko.write_file_txt("__________")

                c.close_file()

            m.close_file()

        f.close_file()

        condition_ok.close_file()
        condition_ko.close_file()

    def export_data_with_mask(self, repo: Repo):

        self.file_mask = FileManager("mask.txt")
        self.file_masked = FileManager("masked.txt")
        self.info = FileManager("info.txt")

        self.file_mask.open_file("a+")
        self.file_masked.open_file("a+")
        self.info.open_file("a+")

        export_dir = os.path.join("export", repo.repository_name + "_" + repo.commit)

        if os.path.exists(export_dir):
            shutil.rmtree(export_dir)

        os.makedirs(export_dir)

        condition_ok = FileManager("condition_ok.txt")
        condition_ok.open_file_txt("a+")
        condition_ko = FileManager("condition_ko.txt")
        condition_ko.open_file_txt("a+")
        repo_status = FileManager("repo_status.txt")
        repo_status.open_file_txt("a+")

        info_repo = list()
        info_repo.append(repo.repository_name)
        info_repo.append(repo.repository_url)
        info_repo.append(repo.commit)

        f = FileManager(os.path.join(export_dir, "repo_info.txt"))
        f.open_file_txt("w+")
        f.write_file_txt("NAME: {}".format(repo.repository_name))
        f.write_file_txt("URL: {}".format(repo.repository_url))
        f.write_file_txt("COMMIT: {}".format(repo.commit))
        f.write_file_txt("IS REPO OK: {}".format(repo.is_repo_ok))
        f.write_file_txt("MESSAGE CLONE: {}".format(repo.message_clone))
        if repo.cloned_directory is not None:
            f.write_file_txt("CLONED DIRECTORY: {}".format(repo.cloned_directory))
        f.write_file_txt("VERSION: {}".format(repo.version))
        f.write_file_txt("IS_TAG: {}".format(repo.is_tag))
        f.close_file()

        repo_status.write_file_txt(
            "{} {} {} {} {} {}".format(repo.repository_name, repo.repository_url, repo.is_repo_ok, repo.message_clone,
                                       repo.version, repo.is_tag))
        repo_status.close_file()

        f = FileManager(os.path.join(export_dir, "list_of_files.txt"))
        f.open_file_txt("w+")
        for file in repo.files:
            f.write_file_txt(file.filename)
            info_file = list()
            info_file.append(file.filename)

            filename = file.filename.split("/")[-1]
            file_without_extension = ".".join(filename.split(".")[:-1])
            file_dir = os.path.join(export_dir, file_without_extension)
            # if we have the same file name in a different path
            if os.path.exists(file_dir):
                base_file_dir = file_dir + "_"
                i = 0
                while os.path.exists(base_file_dir + str(i)):
                    i += 1
                file_dir = base_file_dir + str(i)
            os.makedirs(file_dir, exist_ok=True)

            info_file.append(file_dir)

            shutil.copy(file.filename, os.path.join(file_dir, filename))
            shutil.copy(file.filename.replace(".java", ".xml"),
                        os.path.join(file_dir, filename).replace(".java", ".xml"))
            for i, method in enumerate(file.methods):
                m = FileManager(os.path.join(file_dir, "METHOD_{}.txt".format(i)))

                info_method = list()
                info_method.append("METHOD_{}.txt".format(i))
                info_method.append(method.start)
                info_method.append(method.end)

                m.open_file_txt("w+")
                m.write_file_txt("METHOD START {}, END {}".format(method.start, method.end))
                m.write_file_txt(method.raw_code)
                m.write_file_txt("__________")
                m.write_file_txt(method.text)
                num_ok = 0
                for condition in method.conditions:
                    if condition.is_ok:
                        num_ok += 1
                m.write_file_txt("CONDITIONS OK: {} OUT OF {}".format(num_ok, len(method.conditions)))

                for condition in method.conditions:
                    m.write_file_txt("CONDITION START {}, END {}".format(condition.start, condition.end))
                    m.write_file_txt("IS OK {}, TYPE {}".format(condition.is_ok, condition.type))
                    m.write_file_txt(condition.raw_code)
                    m.write_file_txt("__________")
                    m.write_file_txt(condition.text)

                    if condition.is_ok:
                        condition_ok.write_file_txt(condition.text)
                        condition_ok.write_file_txt("__________")
                        info_condition = list()
                        info_condition.extend(info_repo)
                        info_condition.extend(info_file)
                        info_condition.extend(info_method)
                        info_condition.append(condition.start)
                        info_condition.append(condition.end)
                        info_condition.append(condition.type)
                        self.export_condition_with_data(method, condition, info_condition)
                    else:
                        condition_ko.write_file_txt(condition.text)
                        condition_ko.write_file_txt("__________")

                m.close_file()

        f.close_file()

        condition_ok.close_file()
        condition_ko.close_file()

        self.file_mask.close_file()
        self.file_masked.close_file()
        self.info.close_file()

    def create_file_masked(self, repo: Repo):

        self.file_mask = FileManager("mask.txt")
        self.file_masked = FileManager("masked.txt")
        self.info = FileManager("info.txt")

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
