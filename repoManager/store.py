
from repoManager.repo import Repo
from repoManager.condition import Condition
from repoManager.method import Method

from srcML.srcml_filters import SrcmlFilters

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


    def create_file_masked(self, repo: Repo):

        self.file_mask=FileManager("mask.txt")
        self.file_masked=FileManager("masked.txt")

        self.file_mask.open_file("a+")
        self.file_masked.open_file("a+")

        for file in repo.files:
            for method in file.methods:
                for condition in method.conditions:
                    if condition.is_ok:
                        self.export_condition(method, condition)


        self.file_mask.close_file()
        self.file_masked.close_file()
