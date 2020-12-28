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

from bs4 import BeautifulSoup

import csv


class FileManager:
    def __init__(self, file_path: str):
        '''
        this class is a filemanager. It allows you to read and write txt or csv file
        e.g.
        condition_ok = FileManager("condition_ok.txt")
        condition_ok.open_file_txt("a+")
        condition_ok.write_file_txt("hello!")
        condition_ok.close_file()
        data=condition_ok.read_file_txt()
        '''
        self.file = None
        self.writer = None
        self.fieldnames = None
        self.file_path = file_path
        self.log = settings.logger

    def open_file_csv(self, mode: str, fieldnames: List[str], force_write_header: bool = False):
        write_header = True
        if os.path.exists(self.file_path):
            write_header = False
        self.file = open(self.file_path, mode=mode, encoding="utf-8")
        self.fieldnames = fieldnames
        self.writer = csv.DictWriter(self.file, fieldnames=self.fieldnames)
        if write_header or force_write_header:
            self.writer.writeheader()

    def write_file_csv(self, element_list: List[str]):
        self.writer.writerow(element_list)

    def close_file(self):
        self.file.close()

    def open_file_txt(self, mode: str):
        self.file = codecs.open(self.file_path, mode=mode, encoding="utf-8")

    def read_file_txt(self):
        try:
            self.open_file_txt("r")

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

    def read_csv(self):
        dict_result = dict()
        try:
            with open(self.file_path, mode='r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                line_count = 0
                for row in csv_reader:
                    if line_count == 0:

                        for r in row:
                            dict_result[r] = list()
                            dict_result[r].append(row[r])

                        line_count += 1
                    else:
                        for r in row:
                            dict_result[r].append(row[r])
                        line_count += 1
        except Exception as e:
            dict_result = dict()
        return dict_result

    def write_file_txt(self, element):  # write generic file

        self.file.write(element + "\n")


class Store:
    def __init__(self):
        '''
        this class allows you to export csv files during the json processing of repos
        '''
        self.log = settings.logger

    def export_condition(self, method: Method, condition: Condition, fields: List[str], data: List[str]):
        '''
        this function allows you to export a specific condition. We add a record for each of the following 3 files:
        - mask.txt with the mask part and a <z> token at the end
        - masked.txt with the method without the mask (replaced by a <x> token)
        - info.csv with all information about the two previous files
        '''
        new_condition = SrcmlFilters("<expr>&lt;x&gt;</expr>", True) # new fake condition with <x>

        xml = copy.copy(condition.condition)

        # xml=condition.condition
        condition_start = condition.start
        condition_end = condition.end

        expression = xml.select_one("expr")

        xml.select_one("expr").replaceWith(new_condition.xml_code)

        xml_method = copy.copy(method.xml)

        # find the condition using pos:start and pos:end
        xml_method.find("if", {"pos:end": condition_end, "pos:start": condition_start}).replaceWith(xml)

        # self.log.info("__________")
        # self.log.info("METHOD")
        # self.log.info(xml_method.text)
        # self.log.info("MASK")
        # self.log.info(expression.text)
        # self.log.info("__________")

        self.file_masked.write_file_txt(xml_method.text.replace("\n", " "))
        self.file_mask.write_file_txt(expression.text.replace("\n", " ")+"<z>")

        dict_condition = dict()
        for x, y in zip(fields, data):
            dict_condition[x] = y

        self.info.write_file_csv(dict_condition)

    def export_mask_files(self):
        '''
        This function allows you to mask the whole repos. It is going to create the following 3 files:
        - mask.txt with the mask part and a <z> token at the end
        - masked.txt with the method without the mask (replaced by a <x> token)
        - info.csv with all information about the two previous files
        '''
        self.file_mask = FileManager("mask.txt")
        self.file_masked = FileManager("masked.txt")
        self.info = FileManager("info.csv")

        self.file_mask.open_file_txt("a+")
        self.file_masked.open_file_txt("a+")

        # fields that have to be stored when we export the masked files
        fields_mask_conditions = ["REPO_ID", "REPO_NAME", "REPO_URL", "REPO_COMMIT", "FILE_ID", "FILENAME", "METHOD_ID",
                                  "METHOD_START", "METHOD_END", "CONDITION_ID",
                                                                "CONDITION_START", "CONDITION_END", "CONDITION_TYPE"]

        self.info.open_file_csv("a+", fields_mask_conditions)

        f = FileManager("export/repo_info.csv")
        repo_dict = f.read_csv()

        repos_name = repo_dict["NAME"]
        repos_id = repo_dict["ID"]
        repos_url = repo_dict["URL"]
        repos_commit = repo_dict["COMMIT"]

        for id, name, url, commit in zip(repos_id, repos_name, repos_url, repos_commit):
            f = FileManager("export/{}/file_info.csv".format(id))
            file_dict = f.read_csv()

            if len(file_dict.keys()) == 0:
                continue

            file_ids = file_dict["ID"]
            file_names = file_dict["NAME"]

            self.log.info("logging repo {} - {}".format(id, name))

            for file_id, file_name in zip(file_ids, file_names):
                method_path = "export/{}/{}/method_info.csv".format(id, file_id)
                f = FileManager(method_path)
                method_dict = f.read_csv()

                if len(method_dict.keys()) == 0:
                    continue

                method_ids = method_dict["ID"]
                method_starts = method_dict["START"]
                method_ends = method_dict["END"]

                for method_id, start, end in zip(method_ids,
                                                 method_starts,
                                                 method_ends):
                    condition_path = "export/{}/{}/{}/condition_info.csv".format(id, file_id, method_id)
                    f = FileManager(condition_path)
                    condition_dict = f.read_csv()

                    if len(condition_dict.keys()) == 0:
                        continue

                    condition_ids = condition_dict["ID"]
                    condition_starts = condition_dict["START"]
                    condition_ends = condition_dict["END"]
                    condition_types = condition_dict["TYPE"]
                    condition_isoks = condition_dict["IS_OK"]

                    # create method object
                    method = None
                    try:
                        f = FileManager("export/{}/{}/{}/source.xml".format(id, file_id, method_id))
                        xml = f.read_file_txt()
                        xml = "\n".join(xml)
                        soup = BeautifulSoup(xml, 'lxml')
                        # we have to use this trick to remove <html><body> created by default by BeautifulSoup
                        xml_code_curr = soup.select('body')[0]
                        children = list()
                        for child in xml_code_curr.children:
                            if hasattr(child, "name") and getattr(child, "name") is not None:
                                children.append(getattr(child, "name"))

                        child = children[0]
                        xml_code = xml_code_curr.select(child)[0]

                        method = Method(xml_code, method_id)
                    except Exception as e:
                        continue

                    for condition_id, condition_start, condition_end, condition_type, condition_isok in zip(
                            condition_ids, condition_starts, condition_ends, condition_types, condition_isoks
                    ):
                        if condition_isok == "True":
                            # create condition object
                            condition = None
                            try:
                                f = FileManager(
                                    "export/{}/{}/{}/{}/source.xml".format(id, file_id, method_id, condition_id))
                                xml = f.read_file_txt()
                                xml = "\n".join(xml)
                                soup = BeautifulSoup(xml, 'lxml')

                                xml_code_curr = soup.select('body')[0]

                                children = list()
                                for child in xml_code_curr.children:
                                    if hasattr(child, "name") and getattr(child, "name") is not None:
                                        children.append(getattr(child, "name"))

                                child = children[0]

                                xml_code = xml_code_curr.select(child)[0]

                                condition = Condition(xml_code, condition_id)
                            except Exception as e:
                                continue

                            # info about conditions
                            info_condition = [str(id), name, url, commit, str(file_id), file_name,
                                              str(method_id), start, end, str(condition_id), condition_start,
                                              condition_end, condition_type]
                            self.export_condition(method, condition, fields_mask_conditions, info_condition)

    def export_data(self, repo: Repo):
        '''
        this code allows you to export all information about the repo.
        All the data are stored in 4 different csv:
        - repo_info.csv: general information about each repo
        - file_info.csv: general information about each file
        - method_info.csv: general information about each method
        - condition.csv: general information about each condition
        If a method does not have any condition, the condition.csv will be empty
        '''
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
            values_file = [str(file.id), file.filename, str(len(file.methods))]

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
            fields_method = ["ID", "START", "END", "NUM_CONDITION", "NUM_CONDITION_OK", "ABSTRACTION_REQUIRED",
                             "ABSTRACTION_OK", "NUM_TOKENS", "NUM_LINES", "HAS_NESTED_METHOD"]

            m.open_file_csv("w+", fields_method)

            for i, method in enumerate(file.methods):

                num_ok = 0
                for condition in method.conditions:
                    if condition.is_ok:
                        num_ok += 1

                values_method = [str(method.id), method.start, method.end, str(len(method.conditions)), str(num_ok),
                                 str(method.abstraction_required), str(method.abstraction_ok), str(method.num_tokens),
                                 str(method.num_lines), str(method.has_nested_method)]

                dict_method = dict()
                for x, y in zip(fields_method, values_method):
                    dict_method[x] = y

                m.write_file_csv(dict_method)

                method_dir = os.path.join(file_dir, str(method.id))
                os.makedirs(method_dir, exist_ok=True)
                write_file = FileManager(os.path.join(method_dir, "source.java"))
                write_file.open_file_txt("w+")
                write_file.write_file_txt(method.text)
                write_file.close_file()

                write_file = FileManager(os.path.join(method_dir, "source.xml"))
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

                    values_condition = [str(condition.id), condition.start, condition.end, str(condition.is_ok),
                                        condition.type]

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
