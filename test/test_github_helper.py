import pytest
import shutil
from utils.github_helper import GithubHelper
import os
# from utils.logger import Logger

# @pytest.fixture(scope="session", autouse=True)
# def init():
#     # prepare something ahead of all tests



@pytest.mark.parametrize("repo, cwd, result", [("mciniselli/test", "test_folder/github_helper/output", True),
                                               ("mciniselli/test222", "test_folder/github_helper/output", False)])
def test_clone(repo, cwd, result):


    g = GithubHelper()
    g.clone(repo, cwd)

    r = False

    if len(os.listdir(cwd)) > 0:
        r = True

    if r == result:
        assert True
        return

    assert False


@pytest.mark.parametrize("command, result",
                         [("3.0.1", True), ("3.0a.1", False), (".3.0.1", False), ("3", True), ("3.", False),
                          ("3.23", True)])
def test_is_similar_to_tag(command, result):
    g = GithubHelper()

    res = g.is_similar_to_tag(command)

    if res == result:
        assert True
        return

    assert False


@pytest.mark.parametrize("cwd, result", [("test_folder/github_helper/check_tags_branch/test", "3.0"),
                                               ("test_folder/github_helper/check_tags_branch/test_branch", "3.1")])
def test_get_last_release(cwd, result):

    g = GithubHelper()
    release, is_tag=g.get_last_release(cwd)

    if release==result:
        assert True
        return

    assert False

@pytest.mark.parametrize("cwd, result", [("test_folder/github_helper/check_tags_branch/test", "3.0")])
def test_get_list_of_tags(cwd, result):

    g = GithubHelper()

    res, _=g.get_list_of_tags(cwd)

    res=res.split("\n")[0]
    tag=res.split(" ")[-1]

    if tag==result:
        assert True
        return


    assert False

@pytest.mark.parametrize("cwd, result", [("test_folder/github_helper/check_tags_branch/test", "remotes/origin/3.0.1"),
                                         ("test_folder/github_helper/check_tags_branch/test_branch", "remotes/origin/3.1")])
def test_get_list_of_branches(cwd, result):

    g = GithubHelper()

    res, _=g.get_list_of_branches(cwd)

    res=res.split("\n")
    for r in res:
        if r.strip()==result:
            assert True
            return

    assert False


@pytest.mark.parametrize("repo, cwd", [("mciniselli/test_branch", "test_folder/github_helper/check_tags_branch/TBD"),
                                                  ("mciniselli/test", "test_folder/github_helper/check_tags_branch/TBD")])
def test_checkout(repo, cwd):
    g=GithubHelper()
    g.clone(repo, cwd)

    name=repo.split("/")[-1]
    folder=os.path.join(cwd, name)

    g.checkout(folder)

    files=os.listdir(folder)
    if "TBD.txt" in files:
        assert False
        return

    assert True

