#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Moritz Wundke
import sys
from pslib.tools import main_tool
import rocketeer.tools

__version__ = "0.1"
__author__ = "Moritz Wundke"
__copyright__ = "(c) 2017 Moritz Wundke"
__description__ = "Welcome Rocketeer, a simple script to build your Unreal Engine 4 Rocket distros! - v{version} {copyright} ({author})"

def main():
    return main_tool(sys.argv[1:], description=__description__, author=__author__, copyright=__copyright__, version=__version__)

if __name__ == "__main__":
    sys.exit(main())