
import json

import argparse
from abstraction.abstraction import AbstractionManager

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



def analyse_results(parameter):
    from result_analysis.analysis import Analysis

    a = Analysis()

    a.count_repos()
    result, result_global=a.count_file_and_method()
    print(result)
    print(result_global)

    result, result_global=a.count_file_and_method(*parameter)
    print(result)
    print(result_global)

def abstract_results(parameter):
    abstraction_class=AbstractionManager(0, 100, 5, 15)
    abstraction_class.abstract_mined_repos()

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

    parser.add_argument("-p", "--parameter", type=str, default="0_9999999_0_9999999",
                        help="default parameters for analysis and abstraction. You have to write min number of tokens, max number of tokens,"
                             "min number of lines and max number of lines, separated by a underscore(_). If you do not want to specify"
                             "one of the parameters, put None")

    args = parser.parse_args()

    if args.conditions:
        # -c -s 4 -e 7 -f json_data/results.json
        process_json_file(args.filepath, args.start, args.end, args.do_abstraction_during_check)

    parameter_input = args.parameter.split("_")
    if len(parameter_input) != 4:
        print("ERROR: NUMBER OF PARAMETER IS NOT CORRECT")
        return

    parameter_default=[0, 9999999, 0, 9999999]
    parameter_list=list()

    for default, value in zip(parameter_default, parameter_input):
        if value.lower() == "none":
            parameter_list.append(default)
            continue

        curr=int(value)
        parameter_list.append(curr)

    if args.analysis:
        analyse_results(parameter_list)

    if args.abstract:
        abstract_results(parameter_list)

if __name__=="__main__":
    main()
