#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Moritz Wundke

import os
import sys

from pslib import log_error, log_info, log_warn, EXIT_CODE_FAILED, EXIT_CODE_SUCCESS, run_command
from pslib.tools import register_tool, ITool, ForceSystemExit


#class RocketeerApp(App):
#    kv_directory = 'templates'

@register_tool("gui", "Run Rocketeer in GUI mode")
class GUITool(ITool):
    def __init__(self, parser):
        # actions_parser = parser.add_subparsers(dest='action', help='Actions that you can perform')
        # actions_parser.required = True
        #
        # parser_compile = actions_parser.add_parser('compile', help='Compile QT Designer layouts into python code')
        # parser_compile.add_argument('-p', '--path', help='Root project path', type=str, default='.',
        #                             required=False)
        # parser_compile.add_argument('-o', '--out', help='Out root path where to write out the python files', type=str, default='.',
        #                             required=False)
        # parser_run = actions_parser.add_parser('run', help='Run app in GUI mode')
        pass

    def execute(self, args):
        # if args.action == "compile":
        #     self._compile(os.path.abspath(args.path), os.path.abspath(args.out))
        # elif args.action == "run":
        #     log_warn("Sorry no GUI yet!")
        # else:
        #     log_error("Release action '{}' unkown", args.action)
        #     return EXIT_CODE_FAILED
        # return EXIT_CODE_SUCCESS

        # The kivy app does not handle arguments too well
        sys.argv = sys.argv[:1]
        from rocketeer.tools.gui.rocketeerapp import RocketeerApp
        try:
            RocketeerApp().run()
            sys.exit(EXIT_CODE_SUCCESS)
        except:
            raise ForceSystemExit()

    def _compile(self, src_path, dst_path):

        if not os.path.isdir(src_path):
            raise NotADirectoryError("Directory not found {path}".format(path=src_path))

        if not os.path.isdir(dst_path):
            raise NotADirectoryError("Directory not found {path}".format(path=dst_path))

        for root, dirs, files in os.walk(src_path):
            for file in files:
                if file.endswith(".ui"):
                    self._compile_layout(src_path, dst_path, os.path.join(root, file))

        #log_info(root)
        pass

    # gui compile -p templates -o rocketeer/ui

    def _compile_layout(self, src_path, dst_path, layout):
        compiled = layout.replace(src_path, dst_path)[:-3] + ".py"

        log_info(compiled)
