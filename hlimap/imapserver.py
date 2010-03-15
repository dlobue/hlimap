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
# $Id: imapserver.py 431 2008-12-03 17:49:12Z helder $
#

import socket
from imapfolder import FolderTree
from imaplibii.imapp import IMAP4P

class NoFolderListError(Exception): pass
class NoSuchFolder(Exception): pass

class ImapServer(object):
    '''Establishes the server connection, and does the authentication.
    '''

    def __init__(self, host='localhost', port=None, ssl=False,
        keyfile=None, certfile=None):
        '''
        @param host: host name of the imap server;
        @param port: port to be used. If not specified it will default to 143
            for plain text and 993 for ssl;
        @param ssl: Is the connection ssl?
        @type ssl: Bool
        @param keyfile: PEM formatted private key;
        @param certfile: certificate chain file for the SSL connection.
        '''
        object.__init__(self)

        try:
            self._imap = IMAP4P(host=host, port=port, ssl=ssl,
                keyfile=keyfile,certfile=certfile,  autologout=False )
            self.connected = True
        except socket.gaierror:
            self.connected = False
            raise

        self.special_folders = []
        self.expand_list = []
        self.folder_tree = None

    # IMAP methods
    def login(self, username, password):
        '''Performs the login on the server.

        @param username:
        @param password:

        @return: it returns the LOGIN imap4 command response on the format
            defined on the imaplibii library.
        '''
        return self._imap.login(username, password)

    # Folder list management

    def set_special_folders(self, *folder_list):
        '''The folders are displayed allways with 'INBOX' in the first place,
        then all the folders defined on this method, and then the folders on
        the order returned by the server.
        '''
        self.special_folders = folder_list

    def set_expand_list(self, *folder_list):
        '''From which folders should we fetch the sub folder list?
        '''
        self.expand_list = folder_list

    def refresh_folders(self, subscribed = True):
        '''This method extracts the folder list from the
        server.
        '''
        if not self.folder_tree:
            self.folder_tree = FolderTree( self )

        self.folder_tree.refresh_folders( subscribed )

        self.folder_tree.set_properties(self.expand_list,
                                        self.special_folders)

        self.folder_tree.sort()

        self.set_iterator(self.folder_tree.iter_expand)

    def folder_iter(self):
        '''
        First show the special folders, then rest of the folders
        if a folder is in the expandable list show also the sub folders.
        '''
        return self.folders()

    def set_iterator(self, it):
        '''Pre-defines the iterator to use on the folder tree. The available
        iterators are defined on FolderTree
        '''
        if self.folder_tree:
            self.folders = it
        else:
            raise NoFolderListError('No folder list')

    # Special methods
    def __del__(self):
        '''Logs out from the imap server when the class instance is deleted'''
        if self.connected:
            self._imap.logout()

    def __getitem__(self, path):
        '''Returns a folder object'''
        if not self.folder_tree:
            self.folder_tree = FolderTree( self )

        return self.folder_tree.get_folder(path)

    def __iter__(self):
        '''Iteracts through the folders'''
        if not self.folder_tree:
            self.refresh_folders()

        return self.folders()