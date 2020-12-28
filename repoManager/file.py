from srcML.srcml_manager import SrcmlManager
from srcML.srcml_parser import SrcmlParser
from repoManager.method import Method
import utils.settings as settings
import os
import shutil

class File:
    def __init__(self, filename: str, id: int, abstract: bool = False):
        '''
        this class represents a File. It contains all information about the file itself (included the list of methods)
        '''
        self.methods = list()
        self.filename = filename
        self.id=id
        self.methods = list()
        self.log=settings.logger
        self.abstract=abstract

    def create_abstraction_folder(self):
        os.makedirs("abstraction/temp", exist_ok=True)

    def remove_abstraction_folder(self):
        shutil.rmtree("abstraction/temp", ignore_errors=True)

    def add_methods(self):
        '''
        this function adds all methods contained in the file
        '''
        s = SrcmlManager()
        s.process_with_srcml(self.filename)
        xml_code = s.get_xml()
        p = SrcmlParser(xml_code)
        p.extract_methods()
        self.log.info(len(p.methods))

        for i, m in enumerate(p.methods):
            meth = Method(m, i, self.abstract)
            meth.add_conditions()
            self.methods.append(meth)
