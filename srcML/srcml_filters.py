import sys
import collections
import bs4
import re

class SrcmlFilters():
    def __init__(self, xml_code):
        self.xml_code=xml_code


    def get_list_of_children(self, parent, skip=[None, "block"]):
        children = list()
        for child in parent.children:

            children.append(child.name)
        return [c for c in children if c not in skip]

    def return_unordered_condition(self, list_items):
        dict_cond=dict()
        for l in list_items:
            items=l.split(" ")
            key=int(items[0])
            if key not in dict_cond.keys():
                dict_cond[key]=list()
            dict_cond[key].append(items[1])
        return dict_cond


    def contain_operator_name(self):

        condition=["1 condition", "2 expr", "3 operator", "3 name"]
        dict_cond=self.return_unordered_condition(condition)

        xml_current_level=self.xml_code
        for level in dict_cond.keys():
            level_curr=self.get_list_of_children(xml_current_level)
            if collections.Counter(level_curr) != collections.Counter(dict_cond[level]):
                return False

            xml_current_level=xml_current_level.findChild()

        level_curr = self.get_list_of_children(xml_current_level)
        if len(level_curr)> 0:
            return False

        return True



    def contain_name(self):

        condition=["1 condition", "2 expr", "3 name"]
        dict_cond=self.return_unordered_condition(condition)

        xml_current_level=self.xml_code
        for level in dict_cond.keys():
            level_curr=self.get_list_of_children(xml_current_level)
            if collections.Counter(level_curr) != collections.Counter(dict_cond[level]):
                return False

            xml_current_level=xml_current_level.findChild()

        level_curr = self.get_list_of_children(xml_current_level)
        if len(level_curr)> 0:
            return False

        return True

    def contain_operator_name_literal(self):

        condition=["1 condition", "2 expr", "3 operator", "3 name", "3 literal"]
        dict_cond=self.return_unordered_condition(condition)

        xml_current_level=self.xml_code
        for level in dict_cond.keys():
            level_curr=self.get_list_of_children(xml_current_level)
            if collections.Counter(level_curr) != collections.Counter(dict_cond[level]):
                return False

            xml_current_level=xml_current_level.findChild()

        level_curr = self.get_list_of_children(xml_current_level)
        if len(level_curr)> 0:
            return False

        return True