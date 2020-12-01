import codecs
from utils.command_line import CommandLineHelper

from utils.logger import Logger

class SrcmlManager():
    def __init__(self):
        self.xml_code=None

        self.log_class=Logger()
        self.log=self.log_class.log

    def read_file(self, filepath):  # read generic file
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.readlines()
            c_ = list()
            for c in content:
                r = c.rstrip("\n").rstrip("\r")
                c_.append(r)

        except Exception as e:
            self.log.error("Error ReadFile: " + str(e))
            c_ = []
        return c_

    def process_with_srcml(self, java_path):

        c=CommandLineHelper()
        xml_path=java_path.replace(".java", ".xml")
        file_dir="/".join(java_path.split("/")[:-1])
        cmd="srcml {} -o {}".format(java_path, xml_path)
        c.exec(cmd, file_dir)

        self.xml_code=self.read_file(xml_path)

    def get_xml(self):
        return "\n".join(self.xml_code)
