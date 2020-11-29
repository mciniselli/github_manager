import logging
import os

from utils.command_line import CommandLineHelper

logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s')


class GithubHelper():

    def __init__(self):
        self.cmd = None

    '''

    '''

    def clone(self, repo, directory):

        cmd = 'git clone https://test:test@github.com/{}.git'.format(repo)

        c = CommandLineHelper()
        out, err = c.exec(cmd, directory)

        print(out, err)

        if c.is_command_ok():
            return True

        return False

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

    def get_last_release(self, directory):

        tags, error = self.get_list_of_tags(directory)
        if error:
            return -1
        if len(tags) == 0:
            branches, error = self.get_last_release(directory)
            if error:
                return -1

            branches = branches.split("\n")
            for branch in branches:
                name = branch.split("/")[-1]

        else:
            tags = tags.split("\n")
            last_tag = tags.split(" ")[1]
            print(last_tag)

    def get_list_of_tags(self, directory):
        cmd = "git for-each-ref --sort=-committerdate --format '%(committerdate:unix) %(refname:lstrip=2)' refs/tags"

        c = CommandLineHelper()
        out, err = c.exec(cmd, directory)

        return out, c.is_command_ok()

    def get_list_of_branches(self, directory):
        cmd = "git branch --sort=-committerdate -a"

        c = CommandLineHelper()
        out, err = c.exec(cmd, directory)

        return out, c.is_command_ok()
