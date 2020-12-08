from srcML.srcml_filters import SrcmlFilters
from srcML.srcml_parser import SrcmlParser

import sys

class Method():
    def __init__(self, xml_code):
        self.xml=xml_code
        self.raw_code=xml_code.__str__()

        self.conditions=list()
        self.start=None
        self.end=None
        try:
            self.start=xml_code["pos:start"]
        except Exception as e:
            pass
        try:
            self.end=xml_code["pos:end"]
        except Exception as e:
            pass

        self.add_conditions()

    def add_conditions(self):

        parser=SrcmlParser(self.raw_code)


        if_conditions = parser.extract_all_tags("if", parser.soup)

        print(len(if_conditions))
        for if_condition in if_conditions:
            print(if_condition.text)
            f = SrcmlFilters(if_condition)
            f.print_tree()
            f.apply_all_filters()
            print("_____________________")

    def post_process_token(self, tokens, keep_spaces):
        new_tokens=list()
        for t in tokens:
            if len(t)==0:
                continue
            before_space=False
            after_space=False
            if len(t[0].strip()) == 0:
                before_space=True
            if len(t[-1].strip()) == 0:
                after_space=True

            new_token=t.strip()
            if len(new_token) == 0:
                new_tokens.append(" ")
                continue
            if before_space:
                new_tokens.append(" ")
            new_tokens.append(new_token)
            if after_space:
                new_tokens.append(" ")
        if not keep_spaces:
            new_tokens=[n for n in new_tokens if n != " "]

        return new_tokens
    def extract_list_of_tokens(self, node, keep_spaces=True):
        result = list()
        index_local = 0
        for c in node.recursiveChildGenerator():
            if str(type(c)) == "<class 'bs4.element.NavigableString'>":
                result.append("{}".format(c))
                index_local += 1
        result=self.post_process_token(result, keep_spaces)
        return result
