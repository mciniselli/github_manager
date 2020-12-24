import bs4
from repoManager.store import FileManager
import utils.settings as settings
import codecs
from bs4 import BeautifulSoup


class TokenExtraction:
    def __init__(self, min_tokens: int = 0, max_tokens: int = 9999999, min_lines: int = 0, max_lines: int = 9999999):
        self.min_tokens = min_tokens
        self.max_tokens = max_tokens
        self.min_lines = min_lines
        self.max_lines = max_lines

        self.log = settings.logger

    def read_file(self, filepath):
        '''
        Given a file path @filepath, the function reads the content of the file and, after a rstrip, it returns a list of all lines
        '''
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

    def write_tokens(self, tokens_path, element):  # write generic file

        file = None
        try:
            file = codecs.open(tokens_path, mode='w+', encoding="utf-8")
            file.write(element)

        except Exception as e:
            c_ = []
        finally:
            file.close()

    def tokenized_mined_repos(self):

        f = FileManager("export/repo_info.csv")
        repo_dict = f.read_csv()

        repos_name = repo_dict["NAME"]
        repos_id = repo_dict["ID"]

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

                if len(method_dict.keys()) == 0:
                    continue

                method_ids = method_dict["ID"]
                method_num_tokens = method_dict["NUM_TOKENS"]
                method_num_lines = method_dict["NUM_LINES"]
                method_nested = method_dict["HAS_NESTED_METHOD"]

                self.log.info("logging file {}".format(file_id))

                for method_id, num_tokens, num_lines, nested in zip(method_ids,
                                                                    method_num_tokens,
                                                                    method_num_lines,
                                                                    method_nested):

                    num_tokens = int(num_tokens)
                    num_lines = int(num_lines)
                    if nested == "True":
                        self.log.info("method {}/{}/{} is nested".format(id, file_id, method_id))

                        continue
                    if num_tokens >= self.min_tokens and num_tokens <= self.max_tokens and num_lines >= self.min_lines and num_lines <= self.max_lines:
                        xml_file = "./export/{}/{}/{}/source.xml".format(id, file_id, method_id)
                        tokens_path = "./export/{}/{}/{}/tokens.txt".format(id, file_id, method_id)
                        try:
                            xml = self.read_file(xml_file)
                            xml_code = "\n".join(xml)
                            soup = BeautifulSoup(xml_code, 'lxml')

                            tokens = self.extract_list_of_tokens(soup)
                            self.write_tokens(tokens_path, str(tokens))

                        except Exception as e:
                            self.log.info("method {}/{}/{} FAILED".format(id, file_id, method_id))

                        self.log.info("tokens for method {}/{}/{} written".format(id, file_id, method_id))

    def extract_list_of_tokens(self, node: bs4.element.Tag):
        result = list()
        index_local = 0
        for c in node.recursiveChildGenerator():
            if str(type(c)) == "<class 'bs4.element.NavigableString'>":
                result.append("{}".format(c))
                index_local += 1
        result = [r.strip() for r in result if len(r.strip()) > 0]
        return result
