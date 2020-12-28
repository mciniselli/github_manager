import json

import argparse
from abstraction.abstraction import AbstractionManager
from dataset_creation.dataset_mining import DatasetMining
from token_extraction.token_extraction import TokenExtraction

from utils.settings import init_global


def read_file(filepath):  # read generic file
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.readlines()
        c_ = list()
        for c in content:
            r = c.rstrip("\n").rstrip("\r")
            c_.append(r)

    except Exception as e:
        print("Error ReadFile: " + str(e))
        c_ = []
    return c_


def process_json_file(filepath: str, start: int, end: int, do_abstraction: bool = False):
    json_file = filepath

    file_data = read_file(json_file)
    data = json.loads(file_data[0])
    items = (data["items"])[start:end]
    print(len(items))

    # for i, item in enumerate(items):
    #     print(i, item)

    file_name = "results.json"

    from utils.logger import Logger
    log = Logger("logger.log")

    from repoManager.repo import Repo

    from datetime import datetime
    print(datetime.now())

    for i, item in enumerate(items):
        try:
            print("Processed {} repositories of out {}".format(i + 1, len(items)))
            repo_name = item["name"]
            repo_commit = item["lastCommitSHA"]
            repo_url = "https://github.com/{}".format(repo_name)
            print(repo_url)
            r = Repo(repo_name, repo_url, repo_commit, start + i, do_abstraction)
            r.clone_repo("cloning_folder")
            r.add_files()

            for f in r.files:
                for m in f.methods:
                    m.check_conditions()

            from repoManager.store import Store

            store = Store()
            store.export_data(r)
        except Exception as e:
            print("ERROR {}".format(e))

    print(datetime.now())


def analyse_results(parameter):
    from result_analysis.analysis import Analysis

    a = Analysis()

    a.count_repos()

    result, result_global = a.count_file_and_method(*parameter)

    from repoManager.store import FileManager

    f = FileManager("analysis.txt")
    f.open_file_txt("w+")
    for k in result.keys():
        f.write_file_txt("{}: {}".format(k, result[k]))

    f.close_file()

    f = FileManager("analysis_global.txt")
    f.open_file_txt("w+")
    for k in result_global.keys():
        f.write_file_txt("{}: {}".format(k, result_global[k]))

    f.close_file()

    print(result)
    print(result_global)


def abstract_results(parameter):
    abstraction_class = AbstractionManager(*parameter)
    abstraction_class.abstract_mined_repos()


def export_query(parameter):
    dataset_mining = DatasetMining(*parameter)
    dataset_mining.export_dataset_sql()


def extract_tokens(parameter):
    t = TokenExtraction(*parameter)
    t.tokenized_mined_repos()


def export_mask():
    from repoManager.store import Store

    store = Store()
    store.export_mask_files()


def fix_condition_id():
    '''
    In the first version of the tool, we saved a wrong ID field for conditions.
    With this code we can fix this bug
    '''
    from repoManager.store import FileManager
    import utils.settings as settings
    import os
    import shutil
    '''
    using all csv file generated during methods and conditions abstraction, it is able to abstract all the repos
    '''

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

        settings.logger.info("logging repo {} - {}".format(id, name))

        for file_id in file_ids:
            method_path = "export/{}/{}/method_info.csv".format(id, file_id)
            f = FileManager(method_path)
            method_dict = f.read_csv()

            if len(method_dict.keys()) == 0:
                continue

            method_ids = method_dict["ID"]


            settings.logger.info("logging file {}".format(file_id))

            for method_id in method_ids:
                condition_path = "export/{}/{}/{}/condition_info.csv".format(id, file_id, method_id)
                f = FileManager(condition_path)
                condition_dict = f.read_csv()

                if len(condition_dict.keys()) == 0:
                    continue

                if not os.path.exists(condition_path + "__BACKUP"):
                    shutil.copy(condition_path, condition_path + "__BACKUP")

                fields_condition = ["ID", "START", "END", "IS_OK", "TYPE"]

                c = FileManager(condition_path)

                # we want to force the creation of the header (the file already exists so we'll skip the header otherwise)
                c.open_file_csv("w+", fields_condition, force_write_header=True)

                num_conditions = len(condition_dict["ID"])

                for i in range(num_conditions):

                    values_conditions = list()
                    for field in fields_condition:
                        values_conditions.append(condition_dict[field][i])

                    values_conditions[0] = str(i)

                    dict_row = dict()
                    for x, y in zip(fields_condition, values_conditions):
                        dict_row[x] = y

                    c.write_file_csv(dict_row)

                c.close_file()






def main():
    init_global("logger.log")

    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--start", type=int, default=0,
                        help="The start index for repositories to process")

    parser.add_argument("-e", "--end", type=int, default=0,
                        help="The end index for repositories to process")

    parser.add_argument("-f", "--filepath", type=str, default="json_data/results.json",
                        help="The path of json file")

    parser.add_argument("-c", "--conditions", action="store_true",
                        help="clone the repositories in the json @filepath and check for all conditions")

    parser.add_argument("-a", "--analysis", action="store_true",
                        help="analyze the results")

    parser.add_argument("-do_abstraction_during_check", "--do_abstraction_during_check", action="store_true",
                        help="abstract methods during condition processing")

    parser.add_argument("-abs", "--abstract", action="store_true",
                        help="abstract methods based on repo_info.csv and parameters (see --parameter)")

    parser.add_argument("-exp", "--export_query", action="store_true",
                        help="export all methods in a sql file")

    parser.add_argument("-m", "--mask", action="store_true",
                        help="export all masked files")

    parser.add_argument("-fix", "--fix", action="store_true",
                        help="fix condition file (wrong ID originally reported)")

    parser.add_argument("-p", "--parameter", type=str, default="0_9999999_0_9999999",
                        help="default parameters for analysis and abstraction. You have to write min number of tokens, max number of tokens,"
                             "min number of lines and max number of lines, separated by a underscore(_). If you do not want to specify"
                             "one of the parameters, put None")

    parser.add_argument("-t", "--tokens", action="store_true",
                        help="save tokens")

    args = parser.parse_args()

    if args.conditions:
        # -c -s 4 -e 7 -f json_data/results.json
        process_json_file(args.filepath, args.start, args.end, args.do_abstraction_during_check)

    parameter_input = args.parameter.split("_")
    if len(parameter_input) != 4:
        print("ERROR: NUMBER OF PARAMETER IS NOT CORRECT")
        return

    parameter_default = [0, 9999999, 0, 9999999]
    parameter_list = list()

    for default, value in zip(parameter_default, parameter_input):
        if value.lower() == "none":
            parameter_list.append(default)
            continue

        curr = int(value)
        parameter_list.append(curr)

    if args.analysis:
        analyse_results(parameter_list)

    if args.abstract:
        # -abs -p 0_100_5_15
        abstract_results(parameter_list)

    if args.export_query:
        # -exp -p 0_100_5_15
        export_query(parameter_list)
    if args.tokens:
        extract_tokens(parameter_list)

    if args.mask:
        export_mask()

    if args.fix:
        fix_condition_id()

if __name__ == "__main__":
    main()
