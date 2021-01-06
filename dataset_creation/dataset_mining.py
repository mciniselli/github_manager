from repoManager.store import FileManager
import codecs
import os

import utils.settings as settings


class DatasetMining:
    def __init__(self, min_tokens: int = 0, max_tokens: int = 9999999, min_lines: int = 0, max_lines: int = 9999999, num_max:int = 100):
        '''
        This class allows you to create the sql method table. It contains information about method (e.g. code, abstract_code)
        If you do not have abstracted method, the abstract column will be empty
        You can generate tokens via abstraction or via token_extraction.py file.
        The schema for the database is the following:

        CREATE TABLE IF NOT EXISTS method (
        id_repo INT NOT NULL,
        id_file INT NOT NULL,
        id_method INT NOT NULL,
        code MEDIUMTEXT NOT NULL,
        code_tokens MEDIUMTEXT NOT NULL,
        abstract_code MEDIUMTEXT NOT NULL,
        abstract_representation MEDIUMTEXT NOT NULL,
        repo_name nvarchar(256) NOT NULL,
        repo_url MEDIUMTEXT NOT NULL,
        repo_commit nvarchar(60) NOT NULL,
        file_name MEDIUMTEXT NOT NULL,
        num_methods INT NOT  NULL,
        start_method nvarchar(10) NOT NULL,
        end_method nvarchar(10) NOT NULL,
        num_tokens INT NOT NULL,
        num_lines INT NOT NULL
        );
        '''
        self.min_tokens = min_tokens
        self.max_tokens = max_tokens
        self.min_lines = min_lines
        self.max_lines = max_lines
        self.num_max = num_max
        self.query = list()

        self.log = settings.logger


    def format_string(self, code):
        '''
        format string removing all char that should give problem if imported in sql
        '''
        code_new = code.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n    ")
        return "'{}'".format(code_new)

    def export_query_to_file(self, filename):
        '''
        write the query into @filename
        '''
        file = codecs.open(filename, "w+", "utf-8")
        for q in self.query:
            file.write(q + "\n")
        file.close()

    def read_file_txt(self, file_path):
        '''
        read the file @file_path
        '''
        try:
            with codecs.open(file_path, mode='r', encoding="utf-8") as file:

                content = file.readlines()
                c_ = list()
                for c in content:
                    r = c.rstrip("\n").rstrip("\r")
                    c_.append(r)

        except Exception as e:
            c_ = []
        return c_

    def update_queries(self, rows):
        '''
        create a new query for the entries in @rows and append it to @self.query
        '''
        new_rows = list()
        for records in rows:
            new_rows.append("( {} )".format(", ".join(records)))

        query = "INSERT INTO method (id_repo, id_file, id_method, code, code_tokens, abstract_code, abstract_representation, repo_name, repo_url," \
                "repo_commit, file_name, num_methods, start_method, end_method, num_tokens, num_lines) VALUES {} ;".format(
            ", ".join(new_rows))

        self.query.append(query + '\n')

    def process_map(self, filename):  # write map file in a better way
        '''
        read the mapping generated during abstraction and format it in a more readable way
        '''
        try:
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
            result = list()

            for a, b in zip(lines_type, lines_value):
                types = a.split(",")
                values = b.split(",")
                for a_, b_ in zip(types, values):
                    if len(a_) > 0:
                        result.append(a_ + ": " + b_)
            return str(result)
        except Exception as e:
            return ""

    def export_dataset_sql(self, num_per_query=100):
        '''
        Read all csv containing information about repo and (repo_info.csv, ..).
        Then using that information it retrieves all data about methods and store it in @self.query
        You can choose how many method to insert into a single query
        Information about minimum and maximum number of lines and tokens are used to exclude specific methods.
        '''
        f = FileManager("export/repo_info.csv")
        repo_dict = f.read_csv()

        repos_name = repo_dict["NAME"]
        repos_id = repo_dict["ID"]
        repos_url = repo_dict["URL"]
        repos_commit = repo_dict["COMMIT"]

        rows = list()

        for id, name, url, commit in zip(repos_id, repos_name, repos_url, repos_commit):
            f = FileManager("export/{}/file_info.csv".format(id))
            file_dict = f.read_csv()

            if len(file_dict.keys()) == 0:
                continue

            file_ids = file_dict["ID"]
            file_names = file_dict["NAME"]
            number_methods = file_dict["NUMBER_METHODS"]

            for file_id, file_name, number_method in zip(file_ids, file_names, number_methods):
                method_path = "export/{}/{}/method_info.csv".format(id, file_id)
                f = FileManager(method_path)
                method_dict = f.read_csv()

                if len(method_dict.keys()) == 0:
                    continue

                method_ids = method_dict["ID"]
                method_num_tokens = method_dict["NUM_TOKENS"]
                method_num_lines = method_dict["NUM_LINES"]
                method_nested = method_dict["HAS_NESTED_METHOD"]
                abstraction_required = method_dict["ABSTRACTION_REQUIRED"]
                abstraction_ok = method_dict["ABSTRACTION_OK"]
                starts = method_dict["START"]
                ends = method_dict["END"]

                for method_id, num_tokens, num_lines, nested, already_required, is_abs_ok, start, end in zip(method_ids,
                                                                                                             method_num_tokens,
                                                                                                             method_num_lines,
                                                                                                             method_nested,
                                                                                                             abstraction_required,
                                                                                                             abstraction_ok,
                                                                                                             starts,
                                                                                                             ends):

                    if already_required == 'False' or is_abs_ok == 'False':
                        continue

                    num_tokens = int(num_tokens)
                    num_lines = int(num_lines)
                    if nested == "True":
                        continue

                    if num_tokens >= self.min_tokens and num_tokens <= self.max_tokens and num_lines >= self.min_lines and num_lines <= self.max_lines:
                        java_file = "./export/{}/{}/{}/source.java".format(id, file_id, method_id)
                        abstract_file = "./export/{}/{}/{}/abstract.java".format(id, file_id, method_id)
                        map_file = "./export/{}/{}/{}/abstract.java.map".format(id, file_id, method_id)
                        code_tokens = "./export/{}/{}/{}/tokens.txt".format(id, file_id, method_id)

                        row = list()
                        row.append(str(id))
                        row.append(str(file_id))
                        row.append(str(method_id))
                        row.append(self.format_string("\n".join(self.read_file_txt(java_file))))
                        row.append(self.format_string("\n".join(self.read_file_txt(code_tokens))))
                        row.append(self.format_string("\n".join(self.read_file_txt(abstract_file))))
                        row.append(self.format_string((self.process_map(map_file))))
                        row.append(self.format_string(name))
                        row.append(self.format_string(url))
                        row.append(self.format_string(commit))

                        row.append(self.format_string(file_name))
                        row.append(str(number_method))
                        row.append(self.format_string(start))
                        row.append(self.format_string(end))
                        row.append(str(num_tokens))
                        row.append(str(num_lines))
                        rows.append(row)

                        if len(rows) % num_per_query == 0:
                            self.update_queries(rows)
                            rows = list()

        if len(rows) > 0:
            self.update_queries(rows)
            rows = list()

        self.export_query_to_file("sample.sql")

    def export_dataset_T5_pretrain(self):
        '''
        Read all csv containing information about repo and (repo_info.csv, ..).
        Then using that information it retrieves all data about methods and save in T5_pretrain folder the method
        required for T5 pretraining. It saves also the key.txt file with keys for mapping the data.
        Key is formed by repo_id, file_id and method_id, with an underscore between them
        '''
        f = FileManager("export/repo_info.csv")
        repo_dict = f.read_csv()

        repos_name = repo_dict["NAME"]
        repos_id = repo_dict["ID"]
        repos_url = repo_dict["URL"]
        repos_commit = repo_dict["COMMIT"]

        if not os.path.exists("T5_pretrain"):
            os.makedirs("T5_pretrain")

        key_file_manager = FileManager("T5_pretrain/keys.txt")
        key_file_manager.open_file_txt("w+")

        code_file_manager = FileManager("T5_pretrain/code.txt")
        code_file_manager.open_file_txt("w+")

        for id, name, url, commit in zip(repos_id, repos_name, repos_url, repos_commit):
            f = FileManager("export/{}/file_info.csv".format(id))
            file_dict = f.read_csv()

            if len(file_dict.keys()) == 0:
                continue

            num_methods=0
            do_break = False

            self.log.info("Process repo {} - {}".format(id, name))

            file_ids = file_dict["ID"]
            file_names = file_dict["NAME"]
            number_methods = file_dict["NUMBER_METHODS"]

            for file_id, file_name, number_method in zip(file_ids, file_names, number_methods):
                method_path = "export/{}/{}/method_info.csv".format(id, file_id)
                f = FileManager(method_path)
                method_dict = f.read_csv()

                if len(method_dict.keys()) == 0:
                    continue

                if do_break:
                    break

                method_ids = method_dict["ID"]
                method_num_tokens = method_dict["NUM_TOKENS"]
                method_num_lines = method_dict["NUM_LINES"]
                method_nested = method_dict["HAS_NESTED_METHOD"]

                keys = list()
                codes = list()

                for method_id, num_tokens, num_lines, nested in zip(method_ids,
                                                                    method_num_tokens,
                                                                    method_num_lines,
                                                                    method_nested):
                    num_tokens = int(num_tokens)
                    num_lines = int(num_lines)
                    if nested == "True":
                        continue

                    if num_tokens >= self.min_tokens and num_tokens <= self.max_tokens and num_lines >= self.min_lines and num_lines <= self.max_lines:
                        java_file = "./export/{}/{}/{}/source.java".format(id, file_id, method_id)

                        key = "{}_{}_{}".format(id, file_id, method_id)
                        code = " ".join(self.read_file_txt(java_file))
                        keys.append(key)
                        codes.append(code)

                        num_methods +=1

                        if num_methods >= self.num_max:
                            do_break=True
                            break


                for k in keys:
                    key_file_manager.write_file_txt(k)

                for c in codes:
                    code_file_manager.write_file_txt(c)
