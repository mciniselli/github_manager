from bs4 import BeautifulSoup

from anytree import Node, RenderTree
import anytree
import enum

from typing import List

from utils.logger import Logger
import bs4

'''
We use this class to parametrize all the parameters in the code
'''


class Fields(enum.Enum):
    NAME = "name"
    TEXT = "text"
    IF = "if"
    BLOCK = "block"
    SKIP = [None, BLOCK]

    SPECIAL_TAG = ["name_literal"]
    name_literal = ["name", "literal"]


class KeyValueNode():
    '''
    This class is a single node in the tree. It is made up by the @key (the tag in the xml) and the @value (the text field, "" if missing)
    '''

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __str__(self):
        return "{} {}".format(self.key, self.value)


class SrcmlFilters():
    def __init__(self, xml_code, is_string: str = False):
        '''
        This is the initializer of the SrcmlFilters class. You can call che init function in two different ways:
        1. if you have already created the bs4 xml function, you can pass it to the init with @is_string = False
        2. if you want to pass a string that have to be converted to the bs4 object, you can pass the @xml_code as a string,
        with the paramter @is_string = True
        '''
        xml_code_curr = xml_code

        if is_string:  # this is a bs4 object created by scrml_parser
            xml_code_curr = BeautifulSoup(xml_code, 'lxml')
            '''
            By default bs4 creates an html and body tag if you don't pass the full xml
            In this way we're looking for the body tag to extract the first (an only) child that
            is the tag we're interested in
            '''
            xml_code_curr = xml_code_curr.select('body')[0]
            child = self.get_list_of_children(xml_code_curr)[0]
            xml_code_curr = xml_code_curr.select(child)[0]

        self.xml_code = xml_code_curr
        self.tree = None

        self.log_class = Logger()
        self.log = self.log_class.log

        try:
            '''
            We create the tree
            '''
            text = xml_code_curr.text if hasattr(xml_code_curr, Fields.TEXT.value) else ""

            parent = Node(KeyValueNode(xml_code_curr.name, text))
            self.add_children_to_node_with_text(parent, xml_code_curr, skip=[None, "block"])
            self.tree = parent
        except Exception as e:
            self.log.error("ERROR CREATION TREE")

    def get_list_of_children(self, parent: bs4.element.Tag, skip: bool = Fields.SKIP.value):
        '''
        This function is not used anymore. It allows you to get the list of the children (only name field) of the node @parent
        We use the @skip attribute the exclude from the result specific value we're not interested in
        e.g.
        xml_code = "<xml><function><if>if <condition>(<expr><name>var</name></expr>)</condition></if></function></xml>"
        filters = SrcmlFilters(xml_code, True)
        children=filters.get_list_of_children(filters.xml_code)
        print(len(children))
        '''
        children = list()
        try:
            for child in parent.children:
                if hasattr(child, Fields.NAME.value) and getattr(child, Fields.NAME.value) is not None:
                    children.append(getattr(child, Fields.NAME.value))
            return [c for c in children if c not in skip]
        except Exception as e:
            return list()

    def get_list_of_children_with_text(self, parent: bs4.element.Tag, skip=Fields.SKIP.value):
        '''
        This function allows you to extract the list of the children of the node @parent (a bs4 object)
        We use the @skip attribute the exclude from the result specific value we're not interested in
        e.g.
        xml_code = "<xml><function><if>if <condition>(<expr><name>var</name></expr>)</condition></if></function></xml>"
        filters = SrcmlFilters(xml_code, True)
        children=filters.get_list_of_children_with_text(filters.xml_code)
        print(len(children))
        '''
        children = list()
        try:
            for child in parent.children:
                if hasattr(child, Fields.NAME.value) and getattr(child, Fields.NAME.value) is not None:
                    if hasattr(child, Fields.TEXT.value) and getattr(child, Fields.TEXT.value) is not None:
                        text = getattr(child, Fields.TEXT.value)
                        node = KeyValueNode(getattr(child, Fields.NAME.value), text)
                    else:
                        node = KeyValueNode(getattr(child, Fields.NAME.value), "")
                    children.append(node)
            return [c for c in children if c.key not in skip]
        except Exception as e:
            return list()

    def get_list_of_children_with_text_from_tree(self, parent: anytree.node.node.Node, skip=Fields.SKIP.value):
        '''
        This function allows you to extract the list of the children of the node @parent (a tree node)
        We use the @skip attribute the exclude from the result specific value we're not interested in
        e.g.
        xml_code = "<xml><function><if>if <condition>(<expr><name>var</name></expr>)</condition></if></function></xml>"
        filters = SrcmlFilters(xml_code, True)
        children=filters.get_list_of_children_with_text_from_tree(filters.tree)
        print((children[0]))
        '''
        children = list()
        try:
            for child in parent.children:
                if hasattr(child, Fields.NAME.value) and getattr(child, Fields.NAME.value) is not None:
                    node = getattr(child, Fields.NAME.value)
                    children.append(node)
            return [c for c in children if c.key not in skip]
        except Exception as e:
            return list()

    def add_children_to_node(self, parent: anytree.node.node.Node, xml: anytree.node.node.Node, skip: bool):
        '''
        This function is not used anymore. It allows you to add the children of @xml node (bs4 object) to the node @parent.
        We're considering only the attribute @name
        We use the @skip attribute the exclude from the result specific value we're not interested in
        '''
        children = self.get_list_of_children(xml, skip)
        for child in children:
            c = Node(child, parent=parent)
            xml_new = xml.children
            for c2 in xml_new:
                if c2.name == child:
                    self.add_children_to_node(c, c2, skip)

    def add_children_to_node_with_text(self, parent: anytree.node.node.Node, xml: anytree.node.node.Node, skip):
        '''
        This function allows you to add the children of @xml node (bs4 object) to the node @parent.
        Every node is made up by a key (the tag) and value (the text)
        We use the @skip attribute the exclude from the result specific value we're not interested in
        e.g. in this case we're adding to the children of <xml> all the children of <fake>
        You can use it for merging trees.
        The result is the following
        xml hello
        ├── hello hello
        └── function if (var)
            └── if if (var)
                └── condition (var)
                    └── expr var
                        └── name var
        xml_code = "<xml><hello>hello</hello></xml>"
        xml_code2 = "<fake><function><if>if <condition>(<expr><name>var</name></expr>)</condition></if></function></fake>"

        filters = SrcmlFilters(xml_code, True)

        filters2 = SrcmlFilters(xml_code2, True)

        filters.add_children_to_node_with_text(filters.tree, filters2.tree, [None, "block"])
        filters.print_tree()
        '''
        children = self.get_list_of_children_with_text(xml, skip)
        for child in children:
            c = Node(child, parent=parent)
            xml_new = xml.children
            for c2 in xml_new:
                name = child.key
                if c2.name == name:
                    self.add_children_to_node_with_text(c, c2, skip)

    def print_tree(self):
        '''
        This function allows you to print the tree
        e.g.
        xml_code = "<xml><hello>hello</hello></xml>"
        filters = SrcmlFilters(xml_code, True)
        filters.print_tree()
        '''
        if self.tree == None:
            self.log.info("Please load the tree")
        for pre, fill, node in RenderTree(self.tree):
            self.log.info("%s%s" % (pre, node.name))
            print("%s%s" % (pre, node.name))
        print("-----------")
        self.log.info("--------------")

    def check_condition(self, conditions: List[str]):
        '''
        Given a list of @conditions (a list of strings) this function converts each of them in a SrcmlFilters instance
        and check if the @self.tree has the same structure of at least one of them
        To see further details about how we do the comparison, chdck the function @check_if_tree_are_equal
        e.g.
        xml_code = "<xml><function><if>if <condition>(<expr><name>var</name></expr>)</condition></if></function></xml>"
        filters = SrcmlFilters(xml_code, True)
        conditions = ["<if><condition>(<expr><operator></operator><name></name></expr>)</condition></if>"]
        filters.check_condition(conditions)
        '''
        for condition in conditions:
            comparison_tree = SrcmlFilters(condition, True)
            # comparison_tree.print_tree()
            result = check_if_tree_are_equal(comparison_tree.tree, self.tree, Fields.SKIP.value)

            if result:
                # self.print_tree()
                # comparison_tree.print_tree()
                return True

        return False

    def contain_operator_name(self):
        '''
        This function check if the current condition has the same form of the following sentence (the operator in the sentences
        is an example, we don't care about the operator itself)
        if(!variable_name)
        '''

        conditions = ["<if><condition>(<expr><operator></operator><name></name></expr>)</condition></if>"]
        return self.check_condition(conditions)

    def contain_name(self):
        '''
        This function check if the current condition has the same form of the following sentence
        if(variable_name)
        '''

        conditions = ["<if><condition>(<expr><name></name></expr>)</condition></if>"]
        return self.check_condition(conditions)

    def contain_operator_name_literal(self):
        '''
        This function check if the current condition has the same form of the following sentences (the operator in the sentences
        is an example, we don't care about the operator itself)
        if(variable_name>10)
        if(variable_name==null)
        if(null==variable_name)
        '''
        conditions = [
            "<if><condition>(<expr><name></name><operator></operator><literal></literal></expr>)</condition></if>",
            "<if><condition>(<expr><literal></literal><operator></operator><name></name></expr>)</condition></if>"]
        return self.check_condition(conditions)

    def contain_operator_operator_name_literal(self):
        '''
        This function check if the current condition has the same form of the following sentences(the operator in the sentences
        is an example, we don't care about the operator itself)
        if(variable_name>-1)
        if(literal==+10)
        We check the presence of + or -
        '''
        conditions = [

            "<if><condition>(<expr><name_literal></name_literal><operator></operator><operator>-</operator><name_literal></name_literal></expr>)</condition></if>",
            "<if><condition>(<expr><name_literal></name_literal><operator></operator><operator>+</operator><name_literal></name_literal></expr>)</condition></if>"]

        return self.check_condition(conditions)

    def contain_operator_name_name(self):
        '''
        This function check if the current condition has the same form of the following sentence (the operator in the sentences
        is an example, we don't care about the operator itself)
        if(variable_name==variable_name)
        '''
        conditions = ["<if><condition>(<expr><name></name><operator></operator><name></name></expr>)</condition></if>"]
        return self.check_condition(conditions)

    def contain_equal(self):
        '''
        This function check if the current condition has the same form of the following sentences (the operator in the sentences
        is an example, we don't care about the operator itself)
        if(variable_name.equal(variable_name))
        if(variable_name.equal(variable_name)==True)
        if(!variable_name.equal(variable_name))
        if(!variable_name.equal(variable_name)==True)
        '''
        conditions = [
            "<if><condition>(<expr><operator></operator><call><name><name_literal></name_literal><operator>.</operator><name>equal</name></name><argument_list>(<argument><expr><name_literal></name_literal></expr></argument>)</argument_list></call><operator></operator><name_literal></name_literal></expr>)</condition></if>",
            "<if><condition>(<expr><call><name><name_literal></name_literal><operator>.</operator><name>equal</name></name><argument_list>(<argument><expr><name_literal></name_literal></expr></argument>)</argument_list></call><operator></operator><name_literal></name_literal></expr>)</condition></if>",
            "<if><condition>(<expr><operator></operator><call><name><name_literal></name_literal><operator>.</operator><name>equal</name></name><argument_list>(<argument><expr><name_literal></name_literal></expr></argument>)</argument_list></call></expr>)</condition></if>",
            "<if><condition>(<expr><call><name><name_literal></name_literal><operator>.</operator><name>equal</name></name><argument_list>(<argument><expr><name_literal></name_literal></expr></argument>)</argument_list></call></expr>)</condition></if>"
        ]
        return self.check_condition(conditions)

    def apply_all_filters(self):
        '''
        This function applies all filters to check if @self.tree is equal to one of them
        it returns True if this happens, False otherwise
        e.g.
        xml_code = "<xml><function><if>if <condition>(<expr><name>var</name></expr>)</condition></if></function></xml>"
        filters = SrcmlFilters(xml_code, True)
        filters.apply_all_filters()
        '''
        if self.contain_name():
            print("CONTAIN_NAME")
            return True, "CONTAIN_NAME"

        if self.contain_operator_name():
            print("CONTAIN_OPERATOR_NAME")
            return True, "CONTAIN_OPERATOR_NAME"

        if self.contain_operator_name_name():
            print("CONTAIN_OPERATOR_NAME_NAME")
            return True, "CONTAIN_OPERATOR_NAME_NAME"

        if self.contain_operator_name_literal():
            print("CONTAIN_OPERATOR_NAME_LITERAL")
            return True, "CONTAIN_OPERATOR_NAME_LITERAL"
        if self.contain_operator_operator_name_literal():
            print("CONTAIN_OPEARTOR_OPERATOR_NAME_LITERAL")
            return True, "CONTAIN_OPEARTOR_OPERATOR_NAME_LITERAL"
        if self.contain_equal():
            print("CONTAIN_EQUAL")
            return True, "CONTAIN_EQUAL"

        return False, ""


def equal_value(node_target, node2):
    '''
    This function checks if the @value field of @node_target and @node2 are the same
    If we set the text of the variable in the @node_target (e.g. <name>equal</name>)
    we want to check that this name has to be the same in the @node2 value
    If the value of the @node_target is not present, we don't care about the @node2 value
    '''
    if node_target.name.value.strip() == "":
        return True

    if node_target.name.value.strip() == node2.name.value.strip():
        return True

    return False


def equal_key(node_target, node2):
    '''
    This function check if the @key of @node_target and @node2 is the same
    '''
    if node_target.name.key in Fields.SPECIAL_TAG.value:
        allowed_tags = Fields.__getitem__(node_target.name.key).value
        if node2.name.key in allowed_tags:
            return True
        return False

    return node_target.name.key == node2.name.key


def check_if_tree_are_equal(tree1, tree2, skip):
    '''
    This function checks if the two tree are equal (see @equal_key and @equal_value to see further information about
    what we mean with "equal"
    This is a recursive function so when we refer to "tree" it can be applied to all subtrees of a specific tree
    First of all we extract the list of the child for the two trees (se always exclude the value present in @skip)
    If the length of the child is not the same the trees are not equal
    If both the tree have no children we check if they have the same key and value
    Otherwise, for all the children of both node,
    we check if key and value are the same for each node,
    and if the subtrees are the same
    The function returns True if the trees are equal, False otherwise
    '''
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
