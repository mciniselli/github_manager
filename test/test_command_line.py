from utils.command_line import CommandLineHelper
import pytest
import os


@pytest.mark.parametrize("command, cwd, result", [("ls", "test_folder/command_line", 3),
                                                  ("cat A.txt", "test_folder/command_line", 1)])
def test_exec(command, cwd, result):
    c = CommandLineHelper()
    out, err = c.exec(command, cwd)

    out = out.strip().split("\n")

    if len(out) == result:
        assert True
        return

    assert False


@pytest.mark.parametrize("command, cwd, result", [("ls -la", "test_folder/command_line", True),
                                                  ("lss -la", "test_folder/command_line", False)])
def test_is_command_ok(command, cwd, result):
    c = CommandLineHelper()
    out, err = c.exec(command, cwd)

    command_ok = True
    if len(err) != 0:
        command_ok = False

    print(command_ok)


    if result == command_ok:
        assert True
        return

    assert False
