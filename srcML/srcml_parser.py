from bs4 import BeautifulSoup
from srcML.srcml_filters import SrcmlFilters

from anytree import Node, RenderTree


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
            for if_condition in if_conditions[-1:]:
                print(if_condition.text)
                f = SrcmlFilters(if_condition)
                f.print_tree()
                f.apply_all_filters()
                print("_____________________")

    def apply_filters_if_old(self):



        methods=self.methods
        for m in methods:
            if_conditions=self.extract_all_tags("if", m)

            print(len(if_conditions))
            for if_condition in if_conditions:
                f = SrcmlFilters(if_condition)
                # res=f.contain_operator_name()
                # print(res)
                # parent=Node("if")
                # f.add_children_to_node_with_text(parent, if_condition, skip=[None, "block"])
                #
                # f.tree=parent

                f.print_tree()

                # if (name)
                test = "<if><condition>(<expr><name></name></expr>)</condition></if>"

                # if (!name)
                test="<if><condition>(<expr><operator></operator><name></name></expr>)</condition></if>"

                # of ( name != 10)
                test="<if><condition>(<expr><name></name><operator></operator><literal></literal></expr>)</condition></if>"

                test="<if><condition>(<expr><operator></operator><call><name><name_literal></name_literal><operator>.</operator><name>equal</name></name><argument_list>(<argument><expr><name_literal></name_literal></expr></argument>)</argument_list></call><operator></operator><name_literal></name_literal></expr>)</condition></if>"

                f2 = SrcmlFilters(test, True)


                f2.print_tree()

                # f2=SrcmlFilters(if_condition)

                # parent2=Node("if")
                #
                #
                # f2.add_children_to_node_with_text(parent2, if_condition, skip=[None, "block"])
                #
                # f2.tree=parent2

                # f2.check_if_tree_are_equal(f.tree, f2.tree, [None, "block"], False)
                #
                #
                from srcML.srcml_filters import check_if_tree_are_equal

                rr=check_if_tree_are_equal(f2.tree, f.tree, [None, "block"])

                if rr==1:
                    print(rr)
                    return


