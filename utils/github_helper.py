import os
import shutil
from utils.command_line import CommandLineHelper

from utils.logger import Logger

class GithubHelper():

    def __init__(self):
        self.cmd = None

        self.log_class=Logger()
        self.log=self.log_class.log

    '''
    Clone the repository @repo in the @directory
    '''

    def clone(self, repo, directory):

        shutil.rmtree(directory, ignore_errors=True)
        os.makedirs(directory)

        self.log.info("Cloning repository:")
        cmd = 'git clone https://test:test@github.com/{}.git'.format(repo)
        self.cmd = cmd
        c = CommandLineHelper()
        out, err = c.exec(cmd, directory)

        if c.is_command_ok():
            return True

        return False

    '''
    Check if the branch is similar to a tag (e.g. 3.0.1 is fine, 3.a.1 is not fine)
    '''

    def is_similar_to_tag(self, branch):

        branches = branch.split(".")
        for b in branches:
            if len(b) == 0:
                return False

            if not b.isnumeric():
                return False

        if not branch[0].isnumeric():
            return False

        return True

    '''
    CHeck the last tag of the repo. If the number of tag is 0, we check if there is a branch with a name similar to a tag
    It returns the last release (-1 if not found) and True if is a tag (False if a branch)
    '''

    def get_last_release(self, directory):

        tags, command_ok = self.get_list_of_tags(directory)

        self.log.info("list of tags:")
        self.log.info(str(tags))

        if not command_ok:
            return -1, True
        if len(tags) == 0:
            branches, command_ok = self.get_list_of_branches(directory)
            if not command_ok:
                return -1, True

            branches = branches.split("\n")
            for branch in branches:
                name = branch.split("/")[-1]
                if self.is_similar_to_tag(name):
                    return name, False

            return -1, True

        else:
            tags = tags.split("\n")[0]
            last_tag = tags.split(" ")[-1]

            l.log.info("last tag: {}".format(last_tag))

            return last_tag, True

    '''
    Return the list of all tags (each line has the timestamp and the tag name)
    '''

    def get_list_of_tags(self, directory):
        cmd = "git for-each-ref --sort=-committerdate --format '%(committerdate:unix) %(refname:lstrip=2)' refs/tags"
        self.cmd = cmd
        c = CommandLineHelper()
        out, err = c.exec(cmd, directory)

        return out, c.is_command_ok()

    '''
    Return the list of all branches
    '''

    def get_list_of_branches(self, directory):
        cmd = "git branch --sort=-committerdate -a"
        self.cmd = cmd
        c = CommandLineHelper()
        out, err = c.exec(cmd, directory)
        return out, c.is_command_ok()

    def checkout(self, directory):

        version, is_tag = self.get_last_release(directory)

        cmd = ""
        if is_tag:
            cmd = "git checkout tags/{}".format(version)

        else:
            cmd = "git checkout {}".format(version)

        print(cmd)

        c = CommandLineHelper()
        out, err = c.exec(cmd, directory)
