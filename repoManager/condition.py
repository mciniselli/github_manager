
from srcML.srcml_filters import SrcmlFilters

class Condition:
    def __init__(self, condition):
        self.condition=condition
        self.raw_code=condition.__str__()
        # print(self.raw_code)
        # None = To be checked, True is OK, False is not OK
        self.is_ok=None
        self.type=None

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

        # print("ADDED CONDITION")
        # print(self.condition)
        # print(self.raw_code)

    def check_condition(self):

        f=SrcmlFilters(self.condition)
        f.print_tree()
        result, type=f.apply_all_filters()
        print("___________")

        if result:
            self.is_ok=True
            self.type=type
        else:
            self.is_ok=False
        # for if_condition in if_conditions:
        #     print(if_condition.text)
        #     f = SrcmlFilters(if_condition)
        #     f.print_tree()
        #     f.apply_all_filters()
        #     print("_____________________")