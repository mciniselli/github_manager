from bs4 import BeautifulSoup
from srcML.srcml_filters import SrcmlFilters

class SrcmlParser():
    def __init__(self, xml_code):
        self.methods = list()
        self.xml_code = xml_code
        self.soup = BeautifulSoup(self.xml_code, 'lxml')
        self.contain_if = None

    def extract_all_tags(self, tag, node):
        tags = node.select(tag)
        return tags

    def extract_methods(self):
        self.methods = self.extract_all_tags("function", self.soup)

    def contain_tag(self, tag, node):
        res = self.extract_all_tags(tag, node)
        if len(res) > 0:
            return True
        return False

    def check_contain_if(self, node):
        if self.check_contain_tag("if", node):
            self.contain_if = True
            return
        self.contain_if = False

    def apply_filters_if(self):
        methods=self.methods
        for m in methods:
            if_conditions=self.extract_all_tags("if", m)

            print(len(if_conditions))
            for if_condition in if_conditions:
                print(if_condition.text)
                f = SrcmlFilters(if_condition)
                f.print_tree()
                f.apply_all_filters()
                print("_____________________")