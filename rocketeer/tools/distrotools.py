#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Moritz Wundke

from pslib.tools import register_tool, ITool

@register_tool("distro", "UE4 Distribution tools")
class DistroTool(ITool):
    def __init__(self, parser):
    	pass

    def execute(self, args):
    	print("Sorry no DISTROS yet!")
