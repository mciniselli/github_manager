import pytest
import shutil
from utils.github_helper import GithubHelper
import os


@pytest.mark.parametrize("repo, cwd, result", [("mciniselli/test", "test_folder/github_helper/output", True),
                                               ("mciniselli/test222", "test_folder/github_helper/output", False)])
def test_clone(repo, cwd, result):
    shutil.rmtree(cwd, ignore_errors=True)
    os.makedirs(cwd)

    g = GithubHelper()
    g.clone(repo, cwd)

    r=False

    if len(os.listdir(cwd))>0:
        r=True

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

@pytest.mark.parametrize("repo, cwd, result", [("mciniselli/test", "test_folder/github_helper/output", True),
                                               ("mciniselli/test222", "test_folder/github_helper/output", False)])
def test_get_last_release(repo, cwd, result):
    shutil.rmtree(cwd, ignore_errors=True)
    os.makedirs(cwd)

    g = GithubHelper()
    g.clone(repo, cwd)

    g.get_list_of_tags(cwd)



    assert False


def test_get_list_of_tags():
    assert False


def test_get_list_of_branches():
    assert False
