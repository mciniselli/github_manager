from repoManager.store import FileManager

import utils.settings as settings

class Analysis:
    def __init__(self):
        self.log = settings.logger

    def count_repos(self):
        f = FileManager("export/repo_info.csv")
        result = f.read_csv()

        repos = result["ID"]

        return len(result)

    def count_file_and_method(self, min_token: int = 0, max_token: int = 9999999, min_line: int = 0,
                              max_line: int = 9999999):
        f = FileManager("export/repo_info.csv")
        repo_dict = f.read_csv()

        result = dict()

        repos_name = repo_dict["NAME"]
        repos_id = repo_dict["ID"]
        self.log.info("start counting of files and methods")
        for id, name in zip(repos_id, repos_name):
            self.log.info("processed repo {} {}".format(id, name))
            f = FileManager("export/{}/file_info.csv".format(id))
            file_dict = f.read_csv()

            if len(file_dict.keys()) == 0:
                continue

            file_ids = file_dict["ID"]
            num_files = len(file_ids)

            result[name] = list()
            result[name].append(num_files)

            num_methods_ok = 0

            for file_id in file_ids:
                f = FileManager("export/{}/{}/method_info.csv".format(id, file_id))
                method_dict = f.read_csv()

                if len(method_dict.keys()) == 0:
                    continue

                method_ids = method_dict["ID"]
                method_num_tokens = method_dict["NUM_TOKENS"]
                method_num_lines = method_dict["NUM_LINES"]
                method_nested = method_dict["HAS_NESTED_METHOD"]

                for method_id, num_tokens, num_lines, nested in zip(method_ids, method_num_tokens, method_num_lines,
                                                                    method_nested):
                    num_tokens = int(num_tokens)
                    num_lines = int(num_lines)
                    if nested == True:
                        continue
                    if num_tokens >= min_token and num_tokens <= max_token:
                        if num_lines >= min_line and num_lines <= max_line:
                            num_methods_ok += 1

            result[name].append(num_methods_ok)

        result_global = dict()

        global_num_files = 0
        global_num_methods = 0
        for res in result.keys():
            global_num_files += result[res][0]
            global_num_methods += result[res][1]

        result_global["global_file"] = global_num_files
        result_global["global_method"] = global_num_methods

        return result, result_global
