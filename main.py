
import json

import argparse
from repoManager.store import FileManager
from abstraction.abstraction import Abstraction

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

    file_name="results.json"

    from utils.logger import Logger
    log=Logger("logger.log")

    from repoManager.repo import Repo

    from datetime import datetime
    print(datetime.now())

    for i, item in enumerate(items):
        try:
            print("Processed {} repositories of out {}".format(i+1, len(items)))
            repo_name = item["name"]
            repo_commit = item["lastCommitSHA"]
            repo_url = "https://github.com/{}".format(repo_name)
            print(repo_url)
            r = Repo(repo_name, repo_url, repo_commit, start+i, do_abstraction)
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

def abstract_mined_repos(min_token: int = 0, max_token: int = 9999999, min_line: int = 0,
                              max_line: int = 9999999):

    import utils.settings as settings
    log = settings.logger

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

        log.info("logging repo {} - {}".format(id, name))

        for file_id in file_ids:
            method_path="export/{}/{}/method_info.csv".format(id, file_id)
            f = FileManager(method_path)
            method_dict = f.read_csv()

            if len(method_dict.keys()) == 0:
                continue

            method_ids = method_dict["ID"]
            method_num_tokens = method_dict["NUM_TOKENS"]
            method_num_lines = method_dict["NUM_LINES"]
            method_nested = method_dict["HAS_NESTED_METHOD"]
            abstraction_required=method_dict["ABSTRACTION_REQUIRED"]
            abstraction_ok = method_dict["ABSTRACTION_OK"]

            abstraction_result=list()
            method_to_abstract=list()

            log.info("logging file {}".format(file_id))

            for method_id, num_tokens, num_lines, nested, already_required, is_abs_ok in zip(method_ids, method_num_tokens, method_num_lines,
                                                                method_nested, abstraction_required, abstraction_ok):



                if already_required=='True':
                    abstraction_result.append(is_abs_ok)
                    method_to_abstract.append(already_required)
                    log.info("method {} already abstracted".format(method_id))
                    continue

                num_tokens = int(num_tokens)
                num_lines = int(num_lines)
                if nested == "True":
                    abstraction_result.append(str(True))
                    method_to_abstract.append(str(False))
                    log.info("method {} is nested".format(method_id))

                    continue
                if num_tokens >= min_token and num_tokens <= max_token and num_lines >= min_line and num_lines <= max_line:
                    java_file="./export/{}/{}/{}/source.java".format(id, file_id, method_id)
                    print(java_file)
                    a=Abstraction(java_file)
                    res=a.abstract_method()
                    abstraction_result.append(str(res))
                    method_to_abstract.append(str(True))
                    log.info("method {} abstracted".format(method_id))

                else:
                    abstraction_result.append(str(True))
                    method_to_abstract.append(str(False))
                    log.info("method {} will not be abstracted")


            update_method(method_dict, method_path, method_field, abstraction_result, method_to_abstract)




def update_method(method_dict, method_path, method_field, abstraction_result, method_to_abstract):
    m = FileManager(method_path)

    # we want to force the creation of the header (the file already exists so we'll skip the header otherwise)
    m.open_file_csv("w+", method_field, force_write_header=True)


    num_methods=len(method_dict["ID"])

    for i in range(num_methods):

        values_method=list()
        for field in method_field:
            values_method.append(method_dict[field][i])

        values_method[5]=str(method_to_abstract[i])
        values_method[6]=str(abstraction_result[i])



        dict_row = dict()
        for x, y in zip(method_field, values_method):
            dict_row[x] = y

        m.write_file_csv(dict_row)

    m.close_file()

def analyse_results():
    from result_analysis.analysis import Analysis

    a = Analysis()

    a.count_repos()
    result, result_global=a.count_file_and_method()
    print(result)
    print(result_global)

    result, result_global=a.count_file_and_method(0, 100, 5, 10)
    print(result)
    print(result_global)

    abstract_mined_repos(0, 100, 5, 15)


if __name__=="__main__":
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

    parser.add_argument("-abs", "--do_abstraction", action="store_true",
                        help="abstract methods during condition processing")
    args = parser.parse_args()

    if args.conditions:
        # -c -s 4 -e 7 -f json_data/results.json
        process_json_file(args.filepath, args.start, args.end, args.do_abstraction)

    if args.analysis:
        analyse_results()