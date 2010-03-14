# -*- coding: utf-8 -*-

# hlimap - High level IMAP library
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
# $Id: __init__.py 20 2010-01-15 20:44:48Z hguerreiro $
#

from imapserver import ImapServer

'''High Level IMAP Lib

Introduction
============

This is a high level, object oriented library to handle IMAP connections from
python programs. It aims to hide the awkwardness of the imaplib shipped with
python.

This library only exports the L{ImapServer<ImapServer>} class.

Example Usage
=============

Server Level
------------

First we have to create an instance of L{ImapServer<ImapServer>}, and login only
the server:




'''
