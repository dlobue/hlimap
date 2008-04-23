# -*- coding: utf-8 -*-

# hlimap - high level imap client library
# Copyright (C) 2008 Helder Guerreiro

## This file is part of hlimap.
##
## hlimap is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## hlimap is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with hlimap.  If not, see <http://www.gnu.org/licenses/>.

#
# Helder Guerreiro <helder@paxjulia.com>
#
# $LastChangedDate: 2008-04-09 21:26:21 +0100 (Wed, 09 Apr 2008) $
# $LastChangedRevision: 301 $
# $LastChangedBy: helder $
# 

'''utils module, this is a part of the hlimap IMAP Lib

Utilities.
'''

# Imports

import textwrap

# Classes

class HLError(Exception): pass

# Functions
def quote( str ):
    return '"' + str + '"'
        
def quote( str ):
    return '"' + str + '"'
    
def wrap_lines(text, colnum = 72):
    ln_list = text.split('\n')
    new_list = []
    for ln in ln_list:
        if len(ln) > colnum:
            ln = textwrap.fill(ln, colnum)
        new_list.append(ln)

    return '\n'.join(new_list)
    
    


 

