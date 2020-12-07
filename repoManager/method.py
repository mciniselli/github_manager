

class Method():
    def __init__(self, xml_code):
        self.xml=xml_code

    def extract_list_of_tokens(self, node):
        result = list()
        index_local = 0
        for c in node.recursiveChildGenerator():
            if str(type(c)) == "<class 'bs4.element.NavigableString'>":
                result.append("|{}|".format(c))
                index_local += 1

        return result
