from subprocess import Popen, PIPE, STDOUT
from repoManager.store import FileManager
import utils.settings as settings
import codecs
import shutil
import os

class Abstraction:
    def __init__(self, java_file):
        self.java_file = java_file

        path = self.java_file.split("/")[:-1]
        self.java_abs_file = "/".join(path) + "/abstract.java"
        self.tokens_path="/".join(path) + "/tokens.txt"

    def abstract_method(self):
        try:

            cmd = "java -jar ./abstraction/src2abs-0.1-jar-with-dependencies.jar single method {} {} ./abstraction/Idioms.csv".format(
                self.java_file, self.java_abs_file)

            p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True, cwd=".")
            output = p.stdout.read()
            return True

        except Exception as e:
            return False

    def read_file_txt(self, file_path):
        file = None
        try:
            file=codecs.open(file_path, mode='r', encoding="utf-8")

            content = file.readlines()
            c_ = list()
            for c in content:
                r = c.rstrip("\n").rstrip("\r")
                c_.append(r)

        except Exception as e:
            c_ = []
        finally:
            file.close()
        return c_

    def write_tokens(self, element):  # write generic file

        file = None
        try:
            file=codecs.open(self.tokens_path, mode='w+', encoding="utf-8")
            file.write(element)

        except Exception as e:
            c_ = []
        finally:
            file.close()


    def process_map(self, filename):  # write map file in a better way

        lines = list()
        with codecs.open(filename, "r", "utf-8") as fp:
            for line in fp:
                # print(line)
                if len(line.strip()) > 0:
                    lines.append(line.strip())

        lines_type = list()
        lines_value = list()

        for i, line in enumerate(lines):
            if i % 2 == 0:
                lines_value.append(line)
            else:
                lines_type.append(line)
        result=dict()

        for a, b in zip(lines_type, lines_value):
            types = a.split(",")
            values = b.split(",")
            for a_, b_ in zip(types, values):
                if len(a_) > 0:
                    result[a_] = b_
        return result


    def save_list_of_tokens(self):
        try:
            abstract_file=self.read_file_txt(self.java_abs_file)[0]
            abstract_map_file=self.process_map(self.java_abs_file+".map")
            abstract_tokens=abstract_file.split(" ")
            raw_tokens=list()
            for t in abstract_tokens:
                if t in abstract_map_file.keys():
                    raw_tokens.append(abstract_map_file[t])
                else:
                    raw_tokens.append(t)

            self.write_tokens(str(raw_tokens))
        except Exception as e:
            print("ERROR DURING TOKEN EXTRACTION")

class AbstractionManager:
    def __init__(self, min_tokens: int = 0, max_tokens: int = 9999999, min_lines: int = 0, max_lines: int = 9999999):
        self.min_tokens = min_tokens
        self.max_tokens = max_tokens
        self.min_lines = min_lines
        self.max_lines = max_lines

        self.log = settings.logger

    def abstract_mined_repos(self):

        f = FileManager("export/repo_info.csv")
        repo_dict = f.read_csv()

        repos_name = repo_dict["NAME"]
        repos_id = repo_dict["ID"]

        method_field = ["ID", "START", "END", "NUM_CONDITION", "NUM_CONDITION_OK", "ABSTRACTION_REQUIRED",
                        "ABSTRACTION_OK", "NUM_TOKENS", "NUM_LINES", "HAS_NESTED_METHOD"]

        for id, name in zip(repos_id, repos_name):
            f = FileManager("export/{}/file_info.csv".format(id))
            file_dict = f.read_csv()

            if len(file_dict.keys()) == 0:
                continue

            file_ids = file_dict["ID"]

            self.log.info("logging repo {} - {}".format(id, name))

            for file_id in file_ids:
                method_path = "export/{}/{}/method_info.csv".format(id, file_id)
                f = FileManager(method_path)
                method_dict = f.read_csv()

                if not os.path.exists(method_path+"__BACKUP"):
                    shutil.copy(method_path, method_path+"__BACKUP")

                if len(method_dict.keys()) == 0:
                    continue

                method_ids = method_dict["ID"]
                method_num_tokens = method_dict["NUM_TOKENS"]
                method_num_lines = method_dict["NUM_LINES"]
                method_nested = method_dict["HAS_NESTED_METHOD"]
                abstraction_required = method_dict["ABSTRACTION_REQUIRED"]
                abstraction_ok = method_dict["ABSTRACTION_OK"]

                abstraction_result = list()
                method_to_abstract = list()

                self.log.info("logging file {}".format(file_id))

                for method_id, num_tokens, num_lines, nested, already_required, is_abs_ok in zip(method_ids,
                                                                                                 method_num_tokens,
                                                                                                 method_num_lines,
                                                                                                 method_nested,
                                                                                                 abstraction_required,
                                                                                                 abstraction_ok):

                    if already_required == 'True':
                        abstraction_result.append(is_abs_ok)
                        method_to_abstract.append(already_required)
                        self.log.info("method {} already abstracted".format(method_id))
                        continue

                    num_tokens = int(num_tokens)
                    num_lines = int(num_lines)
                    if nested == "True":
                        abstraction_result.append(str(True))
                        method_to_abstract.append(str(False))
                        self.log.info("method {} is nested".format(method_id))

                        continue
                    if num_tokens >= self.min_tokens and num_tokens <= self.max_tokens and num_lines >= self.min_lines and num_lines <= self.max_lines:
                        java_file = "./export/{}/{}/{}/source.java".format(id, file_id, method_id)
                        # print(java_file)
                        a = Abstraction(java_file)
                        res = a.abstract_method()
                        a.save_list_of_tokens()
                        abstraction_result.append(str(res))
                        method_to_abstract.append(str(True))
                        self.log.info("method {} abstracted".format(method_id))

                    else:
                        abstraction_result.append(str(True))
                        method_to_abstract.append(str(False))
                        self.log.info("method {} will not be abstracted".format(method_id))
                try:
                    self.update_method(method_dict, method_path, method_field, abstraction_result, method_to_abstract)
                except Exception as e:
                    self.log.info("file {} update FAILED ".format(file_id))

    def update_method(self, method_dict, method_path, method_field, abstraction_result, method_to_abstract):
        m = FileManager(method_path)

        # we want to force the creation of the header (the file already exists so we'll skip the header otherwise)
        m.open_file_csv("w+", method_field, force_write_header=True)

        num_methods = len(method_dict["ID"])

        for i in range(num_methods):

            values_method = list()
            for field in method_field:
                values_method.append(method_dict[field][i])

            values_method[5] = str(method_to_abstract[i])
            values_method[6] = str(abstraction_result[i])

            dict_row = dict()
            for x, y in zip(method_field, values_method):
                dict_row[x] = y

            m.write_file_csv(dict_row)

        m.close_file()
