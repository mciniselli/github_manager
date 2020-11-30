from subprocess import Popen, PIPE, STDOUT, TimeoutExpired
import os

import utils.logger as logger

class CommandLineHelper():

    def __init__(self):
        self.cmd=None
        self.output=None
        self.error=None

    '''
    This function execute the command @cmd using @cwd as working directory
    Then save the output in @self.output and the error in @self.error
    At the end return @output and @error
    '''
    def exec(self, cmd, cwd):
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True, cwd=cwd)

        logger.log.info("run command {}".format(cmd))

        try:
            output, error = p.communicate(timeout=60)
        except TimeoutExpired:
            p.kill()
            output, error = p.communicate()

        output = output.decode()
        error = error.decode()
        self.output=output
        self.error=error

        return output, error

    '''
    This function check if previous command is OK, reading the content of @self.error
    '''
    def is_command_ok(self):
        if self.error==None:
            return True
        if len(self.error)==0:
            return True

        return False


