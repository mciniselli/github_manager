from srcML.srcml_manager import SrcmlManager
from srcML.srcml_parser import SrcmlParser
from repoManager.method import Method

class File:
    def __init__(self, filename: str):
        self.methods=None
        self.filename=filename
        self.methods=None

        self.add_methods()

    def add_methods(self):
        s=SrcmlManager()
        s.process_with_srcml(self.filename)
        xml_code=s.get_xml()
        p=SrcmlParser(xml_code)
        p.extract_methods()
        print(len(p.methods))

        methods=list()
        for m in p.methods:
            meth=Method(m)

            methods.append(meth)

        self.methods=methods

        for m in self.methods:
            m.add_conditions()

        # method=methods[0]
        # tokens=method.extract_list_of_tokens(method.xml)
        # for t in tokens:
        #     print(repr(t))
        #
        #
        # method.add_conditions()

