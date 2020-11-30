from utils.command_line import CommandLineHelper

from utils.github_helper import GithubHelper

from utils.logger import *
import utils.logger as logger

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

    g=GithubHelper()
    # g.clone("mciniselli/test", "test/test_folder/github_helper/output")
    # g.checkout("test/test_folder/github_helper/output/test")

    g.clone("mciniselli/test_branch", "test/test_folder/github_helper/output")
    g.checkout("test/test_folder/github_helper/output/test_branch")

if __name__=="__main__":
    init_logger()
    main()