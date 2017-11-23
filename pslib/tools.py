#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Playspace
import inspect
import argparse
import sys

__version__ = "1.0.0"
__author__ = "Moritz Wundke"
__copyright__ = "PlaySpace SL - 2017"
__description__ = "Flexible CLI tool builder - v{version} {copyright} ({author})"

registered_tools = {}
instanced_tools = {}

class ITool:
    def __init__(self, parser):
        raise NotImplementedError('Tool "{}" must implement own __init__(self, parser) method'.format(str(self.__class__)))

    def execute(self, args):
        raise NotImplementedError('Tool "{}" must implement own execute(self) method'.format(str(self.__class__)))

def get_available_tools():
    global registered_tools
    return list(registered_tools.keys())

def init_tools(parser):
    for tool_name in registered_tools:
        tool_parser = parser.add_parser(tool_name, help=registered_tools[tool_name]['help'])
        instanced_tools[tool_name] = registered_tools[tool_name]['cls'](tool_parser)

def execute_tool(tool_name, args):
    global registered_tools
    if tool_name in registered_tools:
        return instanced_tools[tool_name].execute(args)
    raise NotImplementedError('Tool "{}" not registered'.format(tool_name))

def register_tool(name=None, help=None):
    """
    Makes a class to be available as a ITool
    """
    def toolify(cls):
        if inspect.isclass(cls):
            tool_name = name
            if tool_name is None:
                tool_name = cls.__name__
            if tool_name in registered_tools:
                raise NotImplementedError('Tool "{}" with name "{}" already registered'.format(str(cls), tool_name))
            registered_tools[tool_name] = {'cls': cls, 'help': help}
        else:
            raise NotImplementedError('Tool "{}" must be a class if type ITool'.format(str(cls)))
        return cls
    return toolify

def main_tool(argv=None):
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(add_help=True, argument_default=argparse.SUPPRESS, description=__description__.format(version=__version__, copyright=__copyright__, author=__author__))
    parser.add_argument('--clean', action='store_true', default=False, help='Runs the action in clean mode', required=False)
    parser.add_argument('--dryrun', action='store_true', default=False, help='Run the action in dryrun mode', required=False)
    parser.add_argument('--force', action='store_true', default=False, help='Running in force mode will force the action to start in any case', required=False)

    # Add first parser in the nested tree
    subparser = parser.add_subparsers(dest='tool', help='Available tools')
    subparser.required = True
    init_tools(subparser)
    args = parser.parse_args(argv)
    return execute_tool(args.tool, args)
