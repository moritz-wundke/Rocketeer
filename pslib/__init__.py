#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Playspace
#
# Base PS helper lib

import os
import psutil
import sys
import argparse
import shutil
import json
import stat
import time
import subprocess
import uuid
from time import sleep

#
# Consts and globals
#

start_time = []

EXIT_CODE_SUCCESS = 0
EXIT_CODE_FAILED = 1

# ----------------------------------------------------------------------------------------
# Profiling
# ----------------------------------------------------------------------------------------

def time_push():
    global start_time
    start_time.append(time.time())

def time_pop():
    global start_time
    start = start_time.pop() if len(start_time) > 0 else -1
    if start >= 0:
        return time.time() - start
    return 0

# ----------------------------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------------------------

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    LIGHTBLUE = '\033[36m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def xstr(s):
    return '' if s is None else s

def print_safe(s):
    print(s.encode('ascii','replace').decode('ascii'))

def log_info(text, *args):
    print_safe(xstr(text).format(*args))

def log_debug(text, *args):
    print_safe(bcolors.LIGHTBLUE + xstr(text).format(*args) + bcolors.ENDC)

def log_warn(text, *args):
    print_safe(bcolors.WARNING + xstr(text).format(*args) + bcolors.ENDC)

def log_error(text, *args):
    print_safe(bcolors.FAIL + xstr(text).format(*args) + bcolors.ENDC)

def die(text, *args):
    log_error(text, *args)
    sys.exit(EXIT_CODE_FAILED)

# ----------------------------------------------------------------------------------------
# Misc
# ----------------------------------------------------------------------------------------

def to_bool(value):
    return str(value).lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh', 'aye']

def get_uuid():
    return str(uuid.uuid4())

class Bunch(object):
    def __init__(self, adict):
        self.__dict__.update(adict)

    def raw(self):
        return self.__dict__

def ignore_exception(ignored_exceptions=(Exception), default_value=None):
    """ Decorator for ignoring exception from a function
    e.g.   @ignore_exception((DivideByZero))
    e.g.2. ignore_exception((DivideByZero))(Divide)(2/0)
    """
    def dec(function):
        def _dec(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except ignored_exceptions:
                return default_value
        return _dec
    return dec

@ignore_exception(default_value=False)
def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return True

def ensure_not_none(elem):    
    return elem is not None

def ensure_not_empty(elem):
    return elem is not None and elem != ""

def none_if_empty(elem):
    if not ensure_not_empty(elem):
        return None
    return elem

def lower_keys(x):
    if isinstance(x, list):
        return [lower_keys(v) for v in x]
    elif isinstance(x, dict):
        return dict((k.lower(), lower_keys(v)) for k, v in x.items())
    else:
        return x

# ----------------------------------------------------------------------------------------
# File System helpers
# ----------------------------------------------------------------------------------------

def purge_dir(dir_path):
    if os.path.isdir(dir_path):
        log_info("Purging dir {}", dir_path)
        def del_evenReadonly(action, name, exc):
            os.chmod(name, stat.S_IWRITE)
            os.remove(name)
        shutil.rmtree(dir_path, onerror=del_evenReadonly)

def remove_file(file_path):
    if os.path.isfile(file_path):
        log_info("Remove file {}", file_path)
        os.remove(file_path)

def list_dirs(dir_path):
    return [os.path.join(dir_path, dir_name) for dir_name in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, dir_name))]

def list_files(dir_path):
    return [os.path.join(dir_path, file_name) for file_name in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, file_name))]

def copy_file(src, dst):
    try:
        os.remove(dst)
    except:
        pass
    shutil.copy2(src, dst)

def load_json(json_path):
    if not os.path.isfile(json_path) or not os.access(json_path, os.R_OK):
        return None
    with open(json_path, "r") as json_file:
        return json.load(json_file)

def write_json(adict, json_path, pretty=False):
    ensure_dir(os.path.dirname(json_path))
    with open(json_path, 'w') as json_file:
        json.dump(adict, json_file, sort_keys=True, indent=2 if pretty else None)

def write_to_file(text, file_path):
    with open(file_path, "w") as f:
        f.write(text)

def to_unix_path(path):
    return os.path.normpath(path).replace(os.sep, "/")

# ----------------------------------------------------------------------------------------
# OS Helpers
# ----------------------------------------------------------------------------------------

def is_macos():
    return sys.platform.startswith('darwin')

def is_windows():
    return sys.platform.startswith('win')

def kill_proc_tree(pid, including_parent=True):
    parent = psutil.Process(pid)
    for child in parent.children(recursive=True):
        log_info("killing process '{}' with pid '{}' and cmd '{}'", child.name(), child.pid, child.cmdline())
        child.kill()
    if including_parent:
        log_info("killing parent process '{}' with pid '{}' and cmd '{}'", parent.name(), parent.pid, child.cmdline())
        parent.kill()

def get_env_var(var):
    return os.environ[var] if var in os.environ else None

def has_env_var(var):
    return get_env_var(var) is not None

def has_env_var_flag(envvar):
    flag = get_env_var(envvar)
    return True if flag is not None and to_bool(flag) else False

# ----------------------------------------------------------------------------------------
# Process helpers
# ----------------------------------------------------------------------------------------

def run_command(command_args, show_output=True, env=None, cwd=None, return_exit_code=False):
    log_info("Executing command: {}", command_args)
    try:
        if return_exit_code:
            output = subprocess.call(command_args, env=env, cwd=cwd)
        else:
            output = subprocess.check_output(command_args, env=env, cwd=cwd)
        if show_output:
            log_info("{}", output.decode("utf-8", "ignore"))
        return output
    except subprocess.CalledProcessError as e:
        raise Exception("Command '{}' failed with error: {}".format(command_args, e.output.decode("utf-8","ignore")))

@ignore_exception(default_value=-1)
def run_command_safe(command_args, show_output=True, env=None, cwd=None, return_exit_code=False):
    return run_command(command_args, show_output, env, cwd, return_exit_code)

def run_command_retry(command_args, retries, time_between_retries=1, show_output=True, env=None, cwd=None, return_exit_code=False):
    counter = retries
    lastError = None
    counter = max(1, counter)
    while counter > 0:
        try:
            return run_command(command_args, show_output, env, cwd, return_exit_code)
        except Exception as e:
            log_info("Something went wrong executing the command, trying again in {} seconds [{}/{}]", time_between_retries, retries - counter + 1, retries)
            sleep(time_between_retries)
            lastError = e
            counter -= 1
    raise lastError


# ----------------------------------------------------------------------------------------
# Networking helpers
# ----------------------------------------------------------------------------------------

@ignore_exception(default_value="127.0.0.1")
def get_private_ip():
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("google.com",80))
        ip = s.getsockname()[0]
    return ip


# ----------------------------------------------------------------------------------------
# JSON Config helpers
# ----------------------------------------------------------------------------------------

# TODO: Once our Bunch has incasesentive acces we can key.lower()
def get_config(config_dict, key, type, default_value=None):
    return ignore_exception((ValueError), default_value)(type)(config_dict.get(key, default_value))

def get_config_checked(config_dict, key, type, validator, default_value=None):
    config_value = ignore_exception((ValueError), default_value)(type)(config_dict.get(key, default_value))
    if not validator(config_value):
        die("[{}] with value '{}' invalid or not found", key, config_value)
    return config_value

# ----------------------------------------------------------------------------------------
# Input handling
# ----------------------------------------------------------------------------------------

def input(prompt, default):
    import builtins
    return builtins.input("{} [{}]: ".format(prompt, default)) or default

def input_typed(prompt, default, type):
    if not isinstance(default, type):
        raise ValueError("'{}' default value is not of type {}".format(default, type)) 
    return ignore_exception((ValueError), default)(type)(input(prompt, default))

def input_bool(prompt, default):
    return to_bool(input(prompt, default))

def input_float(prompt, default):
    return input_typed(prompt, default, float)

def input_int(prompt, default):
    return input_typed(prompt, default, int)

def input_str(prompt, default):
    return input_typed(prompt, default, str)

# ----------------------------------------------------------------------------------------
# Comandline Application
# ----------------------------------------------------------------------------------------

def ensure_subparser_argument(arg_name, parser, args):
    if not arg_name in args:
        # Get subaction that we are missing and print it's help
        subparsers_actions = [
            action for action in parser._actions 
            if isinstance(action, argparse._SubParsersAction)]

        for subparsers_action in subparsers_actions:
            # get all subparsers and print help
            for choice, subparser in subparsers_action.choices.items():
                if args.which is choice:
                    subparser.print_help()
                    return EXIT_CODE_FAILED

        # Fallback help
        parser.print_help()
        sys.exit(EXIT_CODE_FAILED)

class readable_dir(argparse.Action):
    def __call__(self,parser, namespace, values, option_string=None):
        prospective_dir=values
        if not os.path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError("readable_dir: '{0}' is not a valid dir path".format(prospective_dir))
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace,self.dest,prospective_dir)
        else:
            raise argparse.ArgumentTypeError("readable_dir: '{0} is not a readable dir".format(prospective_dir))

class readable_file(argparse.Action):
    def __call__(self,parser, namespace, values, option_string=None):
        prospective_file=values
        if not os.path.isfile(prospective_file):
            raise argparse.ArgumentTypeError("readable_file: '{0}'' is not a valid file path".format(prospective_file))
        if os.access(prospective_file, os.R_OK):
            setattr(namespace,self.dest,prospective_file)
        else:
            raise argparse.ArgumentTypeError("readable_file: '{0}' is not a readable file".format(prospective_file))
