#! /usr/bin/env python

import os
from os.path import abspath, basename
import sys

from gc3libs import Application
from gc3libs.cmdline import SessionBasedScript
from gc3libs.quantity import GB


if __name__ == '__main__':
    from grayscaler import GrayscaleScript
    GrayscaleScript().run()


class GrayscaleScript(SessionBasedScript):
    """
    Convert images to grayscale.
    """
    def __init__(self):
        super(GrayscaleScript, self).__init__(version='1.0')
    def new_tasks(self, extra):
        # since `self.params.args` is already a list of file names,
        # just iterate over it to build the list of apps to run...
        apps_to_run = []
        for input_file in self.params.args:
            input_file = abspath(input_file)
            apps_to_run.append(GrayscaleApp(input_file, **extra))
        return apps_to_run


# alternatively, you could use
# `from grayscale_app import GrayscaleApp` above
class GrayscaleApp(Application):
    """Convert a single image file to grayscale."""
    def __init__(self, img, **extra):
        inp = basename(img)
        out = "gray-" + inp
        Application.__init__(
            self,
            arguments=[
                "convert", inp, "-colorspace", "gray", out],
            inputs=[img],
            outputs=[out],
            stdout="stdout.txt",
            stderr="stderr.txt",
            **extra)
