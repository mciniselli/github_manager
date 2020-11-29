from utils.command_line import CommandLineHelper

from utils.github_helper import GithubHelper

class Operation():

    def max(values):

      _max = values[0]

      for val in values:
          if val > _max:
              _max = val

      return _max


    def min(values):

      _min = values[0]

      for val in values:
          if val < _min:
              _min = val

      return _min


def main():
    # c=CommandLineHelper()
    # out, err=c.exec("ls", "test/test_folder/command_line")
    # print(len(out))
    # print(out.strip().split("\n"))
    #
    # out, err=c.exec("cat A.txt", "test/test_folder/command_line")
    # print(out)

    g=GithubHelper()

    # res= g.clone("mciniselli/test", "test/test_folder/github_helper/output")
    # print(res)

    tag, err=g.get_list_of_tags("test/test_folder/github_helper/output")
    print(tag)

    out, error=g.get_list_of_tags("preliminary_test/pydriller")

    # out, error=g.get_list_of_branches("preliminary_test/pydriller")
    #
    # print(out)

    # import shutil
    # import os
    # cwd="test/test_folder/github_helper/output"
    # shutil.rmtree(cwd, ignore_errors=True)
    # os.makedirs(cwd)

if __name__=="__main__":
    main()