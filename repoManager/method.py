from srcML.srcml_filters import SrcmlFilters
from srcML.srcml_parser import SrcmlParser
from repoManager.condition import Condition
from typing import List
import os
import bs4
import codecs

from subprocess import Popen, PIPE, STDOUT

import utils.settings as settings
import re


class Method():
    def __init__(self, xml_code: bs4.element.ResultSet, id: int, abstraction: bool = False):
        '''
        this class contains all information about the method itself (included the list of conditions)
        if we pass @abstraction = True we can abstract the method. This operation can be done using abstraction.py file
        in another step
        '''
        self.xml = xml_code
        self.id = id
        self.raw_code = xml_code.__str__()

        self.text = self.xml.text

        self.conditions = list()
        self.start = None
        self.end = None

        self.abstraction_required = abstraction
        self.abstract = None
        self.dict_abstract = None
        self.abstraction_ok = True

        self.num_tokens = len(self.extract_list_of_tokens(self.xml, keep_spaces=False))

        self.num_lines = self.count_lines()

        self.has_nested_method = self.exist_nested_method()

        self.log = settings.logger

        try:
            self.start = xml_code["pos:start"]
        except Exception as e:
            pass
        try:
            self.end = xml_code["pos:end"]
        except Exception as e:
            pass

        if abstraction:
            self.abstract_method()


    def abstract_method(self):
        '''
        this function allows you to abstract the method using Src2Abs
        '''
        try:
            abstraction_folder = "abstraction/temp"
            abstraction_jar = "abstraction"
            self.write_method(abstraction_folder)

            cmd = "java -jar src2abs-0.1-jar-with-dependencies.jar single method ./temp/{}.java ./temp/{}_abs.java ./Idioms.csv".format(
                self.id, self.id)

            p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True, cwd=abstraction_jar)
            output = p.stdout.read()

            f = open(os.path.join(abstraction_folder, "{}_abs.java".format(self.id)), "r")
            self.abstract = f.read()
            f.close()

            f = open(os.path.join(abstraction_folder, "{}_abs.java.map".format(self.id)), "r")
            self.dict_abstract = f.read()
            f.close()

        except Exception as e:
            self.log.error("Error abstraction method {}".format(self.id))
            self.abstraction_ok = False

    def count_lines(self):
        '''
        count the number of lines (lines with less than 3 chars do not count, we remove all the comments)
        '''

        raw_code = self.raw_code

        res = re.sub("(?s)<comment.*?</comment>", "", raw_code);
        res = (re.sub(r'\<[^>]*\>', '', res))

        lines = res.split("\n")

        num_lines = 0
        for line in lines:
            if len(line) > 2:
                num_lines += 1

        return num_lines

    def write_method(self, destination_folder):
        f = codecs.open(os.path.join(destination_folder, "{}.java".format(self.id)), "w+")
        f.write(self.text)
        f.close()

    def add_conditions(self):
        '''
        this function allows you to add all if conditions contained in the method
        '''
        parser = SrcmlParser(self.raw_code)

        if_conditions = parser.extract_all_tags("if", parser.soup)

        for i, if_condition in enumerate(if_conditions):
            self.conditions.append(Condition(if_condition, i))

    def check_conditions(self):
        for condition in self.conditions:
            condition.check_condition()

    def post_process_token(self, tokens: List[str], keep_spaces: bool):
        '''
        This function post process the list of tokens. It removes spaces contained in the tokens
        (e.g. "void " -> "void") and manage the spaces (if we want to consider them as a token)
        '''
        new_tokens = list()
        for t in tokens:
            if len(t) == 0:
                continue
            before_space = False
            after_space = False
            if len(t[0].strip()) == 0:
                before_space = True
            if len(t[-1].strip()) == 0:
                after_space = True

            new_token = t.strip()
            if len(new_token) == 0:
                new_tokens.append(" ")
                continue
            if before_space:
                new_tokens.append(" ")
            new_tokens.append(new_token)
            if after_space:
                new_tokens.append(" ")
        if not keep_spaces:
            new_tokens = [n for n in new_tokens if n != " "]

        return new_tokens

    def extract_list_of_tokens(self, node: bs4.element.Tag, keep_spaces: bool = True):
        '''
        this function allows you to extract the list of all tokens.
        if @keep_spaces = True we consider all spaces as tokens, otherwise we remove them
        '''
        result = list()
        index_local = 0
        for c in node.recursiveChildGenerator():
            if str(type(c)) == "<class 'bs4.element.NavigableString'>":
                result.append("{}".format(c))
                index_local += 1
        result = self.post_process_token(result, keep_spaces)
        return result

    def exist_nested_method(self):
        '''
        this function check if there are other method inside that method (it can happen in java)
        We do not want to process nested methods
        '''
        res = self.xml.select("function")
        res2 = self.xml.select("constructor")
        if len(res) + len(res2) > 0:
            return True
        return False
