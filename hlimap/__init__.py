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

>>> M = ImapServer('example.com')
>>> M.login('example user','example pass')

Folder Level
------------

To get to the messages we have first to examine the folders. The ImapServer 
instance has a property which, dinamicaly, will enable us to access the folders:

>>> folders = M.folders
>>> print folders
<hlimap.imapfolder.Folders object at 0xb7a02fcc>

The folders property is an instance of L{Folders<Folders>}, so we can interact 
through the folders:

>>> for folder in folders:
...     print folder
INBOX.Teste UTF-8 çãáàâ
INBOX.Trash
INBOX.Tretas Maximas
INBOX

Or we can access directly a folder:

>>> inbox = folders['INBOX']
>>> print type(inbox)
<class 'hlimap.imapfolder.Folder'>
>>> print inbox
INBOX

As soon as the L{Folder< Folder>} instance is created, the folder status is 
retrieved from the server. This is stored on a dict:

>>> print inbox.status
{'MESSAGES': 344, 
'mailbox': 'INBOX', 
'UIDNEXT': 31687, 
'UNSEEN': 339, 
'UIDVALIDITY': 1138378795, 
'RECENT': 2}

We can use the methods total, recent and unseen to get the most commonly used 
properies, for instance:

>>> print inbox.total()
344

To be able to further interact with the contents of a folder it's necessary 
to select it:

>>> inbox.select()

The optional responses are parsed and the status is updated. A L{Flags<Flags>}
instance is created with the flag list on the folder and the list of allowed
flags to be saved (permanent flags).

When selecting a folder we check if we have a folder already selected and if so,
we close it before doing the next selection, this way the process is transparent
to the user.

The code can be a bit shortened if we use:

>>> inbox = folders['INBOX'].select()

Which returns a Folder instance, just the same.

>>> print type(inbox)
<class 'hlimap.imapfolder.Folder'>

Message List Level
------------------

Following exactly the same philosofy we can list the messages within the 
folder:

>>> messages = inbox.messages
>>> print type(messages)
<class 'hlimap.imapmessage.Messages'>

Note that the L{Messages<Messages>} class will test the server capabilities and
user the SORT command if possible, and use the SEARCH command otherwise. The 
same is true to the UID commands. That is, if the server has the UIDPLUS 
extension and the SORT extension, it will use both extensions.

We can iteact throgh all the messages on the server, just like we could with 
the folders:

>>> for message in messages:
...    print message

This is not, however, very advisable, since it will force downloading from the
server all the message headers on the folder. This can take some time. So, it's 
best to iteract throgh a slice of the messages. For example:

>>> for message in messages[0:49]:
...     print message

This will iteract through the first 50 messages. Right now, if the server has
the SORT capability, the messages are sorted by SUBJECT and REVERSE DATE. This
will be configurable in the future.

TODO: Set the sort program, also, if we already have the headers then we can 
sort them ourselfs. To do this we have to have a mean of setting the sort 
program that is both understood by the IMAP server and the Messages class. Note
that in the case of a webmail client we can maybe cache the header list between
accesses by the client.

Note that the slice doesn't return a subset of messages, it only returns a 
generator:

>>> print messages[0:49]
<generator object at 0x829506c>

We used this method so that we don't have to fetch a header at a time from the 
server. 

Finnaly, we can get a single message simply by:

>>> print messages['45334']

Message Level
-------------

'''

from main import ImapServer
