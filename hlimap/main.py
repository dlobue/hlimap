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
# $LastChangedDate: 2008-04-28 12:49:27 +0100 (Mon, 28 Apr 2008) $
# $LastChangedRevision: 332 $
# $LastChangedBy: helder $
# 

'''Main module of the hlimap lib

Here we make the connection to the server.
'''

# Global Imports
from imaplibii.imapp import IMAP4P

# Local Imports
from utils import *
from imapfolder import FolderTree

class ImapServer(object):
    '''Establishes the server connection, and does the authentication. 
    Currently we are able to connect through ssl or not.
    '''
    
    def __init__(self, host='localhost', port=None, ssl=False, 
        stream=False, keyfile=None, certfile=None):
        '''
        @param host: host name of the imap server, or command to initiate
            pre-authenticated tunnel;
        @param port: port to be used. If not specified it will default to 143 
            for plain text and 993 for ssl;
        @param ssl: Is the connection ssl?
        @type ssl: Bool
        @param stream: Is this a pre-authenticated stream?
        @type stream: Bool
        @param keyfile: PEM formatted private key;
        @param certfile: certificate chain file for the SSL connection.
        '''
        object.__init__(self)
        
        self._imap = IMAP4P(host=host, port=port, ssl=ssl, 
            stream=stream, keyfile=keyfile,certfile=certfile )
        
        self._folders = None
        self.sstatus = self._imap.sstatus
        
    def login(self, username, password):
        '''Performs the login on the server.
        
        @param username: 
        @param password:
        
        @return: it returns the LOGIN imap4 command response on the format 
            defined on the imaplibii library.
        '''
        return self._imap.login(username, password)
            
    def logout(self):
        '''Performs the logout from the server. 
        
        Please note that as soon as the IMAP4P object is destroied an automatic
        logout is performed. Because of this, this method should only be used 
        if one wants to reuse the instance to make another login, other wise
        it's best to destroy the instance and let the destructor do the logout.
        
        @return: it returns the LOGOUT imap4 command response on the format 
            defined on the imaplibii library.
        '''
        return self._imap.logout()
               
    def getFolders(self):
        '''This is a getter to the folders property.
        
        @return: a L{Folders<Folders>} instance.
        '''
        if not self._folders:
            self._folders = FolderTree(self._imap)
        return self._folders
       
    folders = property(getFolders, None, None, (
    'Folder structer on the account.'
    'This is used to access the folders and messages.'))
