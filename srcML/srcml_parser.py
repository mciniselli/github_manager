from bs4 import BeautifulSoup
from srcML.srcml_filters import SrcmlFilters
import bs4
from utils.logger import Logger

class SrcmlParser():
    def __init__(self, xml_code):
        self.methods = list()
        self.xml_code = xml_code
        self.soup = BeautifulSoup(self.xml_code, 'lxml')
        self.contain_if = None

        self.log_class = Logger()
        self.log = self.log_class.log

    def extract_all_tags(self, tag: str, node: bs4.element.Tag):
        '''
        This function use the select operator defined by beautifulsoup to return the list of all tag @tag
        inside the node @node
        We can choose every node
        e.g.
        xml_code="<xml><function><if>if <condition>(<expr><name>var</name></expr>)</condition></if></function></xml>"
        parser=SrcmlParser(xml_code)
        tags=parser.extract_all_tags("if", parser.soup)
        print(len(tags))
        '''

        tags = node.select(tag)
        return tags

    def extract_methods(self):
        '''
        This function uses the @extract_all_tags method to extract all methods contained in the xml file
        e.g.
        xml_code = "<xml><function><if>if <condition>(<expr><name>var</name></expr>)</condition></if></function></xml>"
        parser = SrcmlParser(xml_code)
        parser.extract_methods()
        print(len(parser.methods))
        '''
        self.methods = self.extract_all_tags("function", self.soup)

    def check_contain_tag(self, tag: str, node: bs4.element.Tag):
        '''
        This function uses the @extract_all_tags method to check if there are some tag @tag inside the node
        e.g.
        xml_code = "<xml><function><if>if <condition>(<expr><name>var</name></expr>)</condition></if></function></xml>"
        parser = SrcmlParser(xml_code)
        result=parser.check_contain_tag("condition", parser.soup)
        print(result)
        '''
        res = self.extract_all_tags(tag, node)
        if len(res) > 0:
            return True
        return False

    def check_contain_if(self, node: bs4.element.Tag):
        '''
        This function checks if there are some if tag in the node @node
        e.g.
        xml_code = "<xml><function><if>if <condition>(<expr><name>var</name></expr>)</condition></if></function></xml>"
        parser = SrcmlParser(xml_code)
        parser.check_contain_if(parser.soup)
        print(parser.contain_if)
        '''
        self.contain_if = self.check_contain_tag("if", node)

    def apply_filters_if(self):
        '''
        This is the main function. It takes the list of methods and for each method it extracts all the "if" conditions
        Then, for each if condition, it applies the @SrcmlFilters.apply_all_filters function to check if that condition is
        belonging to one of the classes we're searching
        e.g.
        xml_code = "<xml><function><if>if <condition>(<expr><name>var</name></expr>)</condition></if></function></xml>"
        parser = SrcmlParser(xml_code)
        parser.extract_methods()
        parser.apply_filters_if()
        '''
        methods=self.methods
        for m in methods:
            if_conditions=self.extract_all_tags("if", m)

            # print(len(if_conditions))
            for if_condition in if_conditions:

                # print(if_condition.text)
                f = SrcmlFilters(if_condition)
                # f.print_tree()
                f.apply_all_filters()
                # print("_____________________")