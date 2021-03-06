
from srcML.srcml_filters import SrcmlFilters

from utils.logger import Logger
import bs4
import utils.settings as settings

class Condition:
    def __init__(self, condition: bs4.element.ResultSet, id: int):
        '''
        this class allows you to deal with conditions. We save the bs4 object, the raw xml code and the text
        '''
        self.condition=condition
        self.raw_code=condition.__str__()
        self.text=condition.text
        self.id=id
        # print(self.raw_code)
        # None = To be checked, True is OK, False is not OK
        self.is_ok=None
        self.type=None


        self.srcml_filter=None

        self.start=None
        self.end=None
        try:
            self.start=condition["pos:start"]
        except Exception as e:
            pass
        try:
            self.end=condition["pos:end"]
        except Exception as e:
            pass
        self.log = settings.logger

        # print("ADDED CONDITION")
        # print(self.condition)
        # print(self.raw_code)

    def print_condition(self):
        self.log.info("----------")
        self.log.info(self.text)
        self.log.info(self.condition)
        self.log.info("IS OK: {}, TYPE: {}".format(self.is_ok, self.type))

        self.log.info("----------")


    def check_condition(self):
        '''
        this function calls a SrcmlFilter function to classify it in one of the categories we are interested into
        '''
        f=SrcmlFilters(self.condition)

        self.srcml_filter=f

        # f.print_tree()
        result, type=f.apply_all_filters()

        if result:
            self.is_ok=True
            self.type=type
            self.print_condition()
        else:
            self.is_ok=False