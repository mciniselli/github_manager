from bs4 import BeautifulSoup

from anytree import Node, RenderTree
from anytree.exporter import JsonExporter

import enum


# Using enum class create enumerations
class Fields(enum.Enum):
    NAME = "name"
    TEXT = "text"
    IF = "if"
    BLOCK = "block"
    SKIP = [None, BLOCK]

    SPECIAL_TAG = ["name_literal"]
    name_literal = ["name", "literal"]


class KeyValueNode():
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __str__(self):
        return "{} {}".format(self.key, self.value)


class SrcmlFilters():
    def __init__(self, xml_code, is_string=False):

        xml_code_curr = xml_code

        if is_string:  # this is a bs4 object created by scrml_parser
            xml_code_curr = BeautifulSoup(xml_code, 'lxml')

            xml_code_curr = xml_code_curr.select('body')[0]
            child = self.get_list_of_children(xml_code_curr)[0]
            xml_code_curr = xml_code_curr.select(child)[0]

        self.xml_code = xml_code_curr
        self.tree = None

        try:

            text = ""
            if hasattr(xml_code_curr, Fields.TEXT.value):
                text = xml_code_curr.text

            parent = Node(KeyValueNode(xml_code_curr.name, xml_code_curr.text))
            self.add_children_to_node_with_text(parent, xml_code_curr, skip=[None, "block"])
            self.tree = parent
        except Exception as e:
            print("ERROR CREATION TREE")

    def get_list_of_children(self, parent, skip=Fields.SKIP.value):
        children = list()
        try:
            for child in parent.children:
                if hasattr(child, Fields.NAME.value) and child.name is not None:
                    children.append(child.name)
            return [c for c in children if c not in skip]
        except Exception as e:
            return list()

    def get_list_of_children_with_text(self, parent, skip=Fields.SKIP.value):
        children = list()
        try:
            for child in parent.children:
                if hasattr(child, Fields.NAME.value) and child.name is not None:  # check if child["name"]
                    if hasattr(child, Fields.TEXT.value) and child.text is not None:
                        text = child.text
                        node = KeyValueNode(child.name, text)
                    else:
                        node = KeyValueNode(child.name, "")
                    children.append(node)
            return [c for c in children if c.key not in skip]
        except Exception as e:
            return list()

    def get_list_of_children_with_text_from_tree(self, parent, skip=Fields.SKIP.value):
        children = list()
        try:
            for child in parent.children:
                if hasattr(child, Fields.NAME.value) and child.name is not None:
                    node = child.name
                    children.append(node)
            return [c for c in children if c.key not in skip]
        except Exception as e:
            return list()

    def add_children_to_node(self, parent, xml, skip):
        children = self.get_list_of_children(xml, skip)
        for child in children:
            c = Node(child, parent=parent)
            xml_new = xml.children
            for c2 in xml_new:
                if c2.name == child:
                    self.add_children_to_node(c, c2, skip)

    def add_children_to_node_with_text(self, parent, xml, skip):
        children = self.get_list_of_children_with_text(xml, skip)
        for child in children:
            c = Node(child, parent=parent)
            xml_new = xml.children
            for c2 in xml_new:
                name = child.key
                if c2.name == name:
                    self.add_children_to_node_with_text(c, c2, skip)

    def print_tree(self):
        if self.tree == None:
            print("Please load the tree")
        for pre, fill, node in RenderTree(self.tree):
            print("%s%s" % (pre, node.name))

    def check_condition(self, conditions):
        for condition in conditions:
            comparison_tree = SrcmlFilters(condition, True)
            # comparison_tree.print_tree()
            result = check_if_tree_are_equal(comparison_tree.tree, self.tree, Fields.SKIP.value)

            if result:
                # self.print_tree()
                comparison_tree.print_tree()
                return True

        return False

    def contain_operator_name(self):

        # if (!name)
        conditions = ["<if><condition>(<expr><operator></operator><name></name></expr>)</condition></if>"]
        return self.check_condition(conditions)

    def contain_name(self):

        # if (name)
        conditions = ["<if><condition>(<expr><name></name></expr>)</condition></if>"]
        return self.check_condition(conditions)

    def contain_operator_name_literal(self):
        # if ( name != 10)
        conditions = [
            "<if><condition>(<expr><name></name><operator></operator><literal></literal></expr>)</condition></if>",
            "<if><condition>(<expr><literal></literal><operator></operator><name></name></expr>)</condition></if>"]
        return self.check_condition(conditions)

    def contain_operator_name_name(self):

        # if ( name != name2 )
        conditions = ["<if><condition>(<expr><name></name><operator></operator><name></name></expr>)</condition></if>"]
        return self.check_condition(conditions)

    def contain_equal(self):

        conditions = [
            "<if><condition>(<expr><operator></operator><call><name><name_literal></name_literal><operator>.</operator><name>equal</name></name><argument_list>(<argument><expr><name_literal></name_literal></expr></argument>)</argument_list></call><operator></operator><name_literal></name_literal></expr>)</condition></if>",
            "<if><condition>(<expr><call><name><name_literal></name_literal><operator>.</operator><name>equal</name></name><argument_list>(<argument><expr><name_literal></name_literal></expr></argument>)</argument_list></call><operator></operator><name_literal></name_literal></expr>)</condition></if>",
            "<if><condition>(<expr><operator></operator><call><name><name_literal></name_literal><operator>.</operator><name>equal</name></name><argument_list>(<argument><expr><name_literal></name_literal></expr></argument>)</argument_list></call></expr>)</condition></if>",
            "<if><condition>(<expr><call><name><name_literal></name_literal><operator>.</operator><name>equal</name></name><argument_list>(<argument><expr><name_literal></name_literal></expr></argument>)</argument_list></call></expr>)</condition></if>"
        ]
        return self.check_condition(conditions)

    def apply_all_filters(self):
        if self.contain_name():
            print("CONTAIN_NAME")
            return True

        if self.contain_operator_name():
            print("CONTAIN_OPERATOR_NAME")
            return True

        if self.contain_operator_name_name():
            print("CONTAIN_OPERATOR_NAME_NAME")
            return True

        if self.contain_operator_name_literal():
            print("CONTAIN_OPERATOR_NAME_LITERAL")
            return True

        if self.contain_equal():
            print("CONTAIN_EQUAL")
            return True

        return False


def equal_value(node_target, node2):
    if node_target.name.value == "":
        return True

    if node_target.name.value.strip() == node2.name.value.strip():
        return True

    return False


def equal_key(node_target, node2):
    if node_target.name.key in Fields.SPECIAL_TAG.value:
        allowed_tags = Fields.__getitem__(node_target.name.key).value
        if node2.name.key in allowed_tags:
            return True
        return False

    return node_target.name.key == node2.name.key


def check_if_tree_are_equal(tree1, tree2, skip):
    child_1 = [t for t in tree1.children if t.name.key not in skip]
    child_2 = [t for t in tree2.children if t.name.key not in skip]

    if len(child_1) != len(child_2):
        return False

    if len(child_1) == 0 and len(child_2) == 0:
        return equal_key(tree1, tree2) and equal_value(tree1, tree2)

    result = True

    for x, y in zip(child_1, child_2):
        res_key = equal_key(x, y)
        res_value = equal_key(x, y)

        res = check_if_tree_are_equal(x, y, skip)
        result = result * res and res_key and res_value

    return result
