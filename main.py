
import json

import argparse

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


def analyse_results():
    from result_analysis.analysis import Analysis

    a = Analysis()

    a.count_repos()
    result, result_global=a.count_file_and_method()

    print(result)
    print(result_global)


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