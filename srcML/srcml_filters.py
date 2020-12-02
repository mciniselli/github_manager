import sys
import collections
import bs4
import re
import json

from bs4 import BeautifulSoup

from anytree import Node, RenderTree
from anytree.exporter import JsonExporter

#usare enumerate o simile come chiave valore  if -> enum.if


NAME = "name"
TEXT = "text"
IF = "if"
BLOCK = "block"
SKIP=[None, BLOCK]

class KeyValueNode():
    def __init__(self, key, value):
        self.key = key
        self.value=value

    def __str__(self):
        return "{} {}".format(self.key, self.value)

class SrcmlFilters():
    def __init__(self, xml_code, is_string=False):

        xml_code_curr=xml_code

        if is_string: # this is a bs4 object created by scrml_parser
            xml_code_curr = BeautifulSoup(xml_code, 'lxml')
            xml_code_curr=xml_code_curr.select('if')[0]

        self.xml_code=xml_code
        self.tree=None

        try:
            parent = Node(xml_code_curr.name)
            self.add_children_to_node_with_text(parent, xml_code_curr, skip=[None, "block"])
            self.tree = parent
        except Exception as e:
            print("ERROR CREATION TREE")


    def get_list_of_children(self, parent, skip=SKIP):
        children = list()
        try:
            for child in parent.children:
                if hasattr(child, NAME) and child.name is not None:
                    children.append(child.name)
            return [c for c in children if c not in skip]
        except Exception as e:
            return list()


    def get_list_of_children_with_text(self, parent, skip=SKIP):
        children = list()
        try:
            for child in parent.children:
                if hasattr(child, NAME) and child.name is not None:
                    if hasattr(child, TEXT) and child.text is not None:
                        text=child.text
                        node=KeyValueNode(child.name, text)
                    children.append(node) # change in tuple using a object
            return [c for c in children if c.key not in skip]
        except Exception as e:
            return list()


    def add_children_to_node(self, parent, xml, skip):
        children=self.get_list_of_children(xml, skip)
        for child in children:
            c=Node(child, parent=parent)
            xml_new = xml.children
            for c2 in xml_new:
                if c2.name==child:
                    self.add_children_to_node(c, c2, skip)


    def add_children_to_node_with_text(self, parent, xml, skip):
        children=self.get_list_of_children_with_text(xml, skip)
        for child in children:
            c=Node(child, parent=parent)
            xml_new = xml.children
            for c2 in xml_new:
                name=child.key
                if c2.name==name:
                    self.add_children_to_node_with_text(c, c2, skip)

    def print_tree(self):
        if self.tree==None:
            print("Please load the tree")
        for pre, fill, node in RenderTree(self.tree):
            print("%s%s" % (pre, node.name))





    def contain_operator_name(self):

        condition=["1 condition", "2 expr", "3 operator", "3 name"]
        return self.check_condition(condition)


    def contain_name(self):

        condition = "<if>if <condition>(<expr><name>test</name></expr>)</condition></if>"
        pattern = SrcmlFilters(condition, True)
        check_if_tree_are_equal(pattern.tree, self.tree, SKIP)

        return self.check_condition(condition)

    def contain_operator_name_literal(self):

        condition=["1 condition", "2 expr", "3 operator", "3 name", "3 literal"]
        return self.check_condition(condition)

    def contain_operator_name_name(self):

        condition=["1 condition", "2 expr", "3 operator", "3 name", "3 name"]
        return self.check_condition(condition)

    '''
        <if_stmt><if>if <condition>(<expr><operator>!</operator><call><name><name>cde</name><operator>.</operator><name>equal</name></name><argument_list>(<argument><expr><name>TEST</name></expr></argument>, <argument><expr><name>TEST</name></expr></argument>)</argument_list></call> <operator>&gt;</operator> <name>test</name></expr>)</condition><block>{<block_content>
        <return>return <expr><name>range</name></expr>;</return>
		</block_content>}</block></if></if_stmt>
    '''

    def contain_equal(self):
        condition=["1 condition", "2 expr", "3 operator", "3 call", "4 call", "5 name", "6 name", "6 operator", "6 name"]

def equal_leaf(leaf1, leaf2):
    if leaf1.value == "":
        return True

    if leaf1.value == leaf2.value:
        return True

    return False




def check_if_tree_are_equal(tree1, tree2, skip):

    if tree1.children == None and tree2.children == None:
        return equal_leaf(tree1, tree2)

    child_1=[t for t in tree1.children if t.name.key not in skip]
    child_2=[t for t in tree2.children if t.name.key not in skip]

    if len(child_1) != len(child_2):
        return False

    result=True

    for x, y in zip(child_1, child_2):
        res=check_if_tree_are_equal(x,y, skip)
        result*=res

    return result


