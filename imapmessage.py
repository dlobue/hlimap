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
# $LastChangedDate: 2008-04-22 18:11:26 +0100 (Tue, 22 Apr 2008) $
# $LastChangedRevision: 326 $
# $LastChangedBy: helder $
# 

'''imapmessage module, this is a part of the hlimap IMAP Lib

Message handling classes. Everything related to messages is handled here.
'''

# Imports
import email, base64, quopri
import datetime
import textwrap
import pprint

# Local imports
from utils import *

# System flags
DELETED = r'\Deleted'
SEEN = r'\Seen'
ANSWERED = r'\Answered'
FLAGGED = r'\Flagged'
DRAFT = r'\Draft'
RECENT = r'\Recent'

# Classes
class Message(object):
    def __init__(self, IMAP, folder, uid, info):
        '''info as the form
        
        According to the RFC we have::
        
            envelope   = "(" env-date SP env-subject SP env-from SP
                          env-sender SP env-reply-to SP env-to SP env-cc SP
                          env-bcc SP env-in-reply-to SP env-message-id ")"
                          
        '''
        object.__init__(self)
        
        self._imap = IMAP
        self.folder = folder
        self.uid = uid
        self.internal_date = info['INTERNALDATE']
        self.size = info['RFC822.SIZE']
        self.setFlags(info['FLAGS'])
        
        self.envelope = info['ENVELOPE']

        self.show_subtype = 'PLAIN' # Show only TEXT/PLAIN parts
        
        self.__bodystructure = None
        
    def get_bodystructure(self):
        if not self.__bodystructure:
            self.__bodystructure = self._imap.fetch_smart(self.uid, 
                '(BODYSTRUCTURE)')[self.uid]['BODYSTRUCTURE']
        return self.__bodystructure
    bodystructure = property(get_bodystructure)  
    
    def part(self, part):
        '''Get a part from the server.
        '''
        query = part.query()
        text = self.fetch(query)

        if part.body_fld_enc == 'BASE64':
            text = base64.b64decode(text )
        elif part.body_fld_enc == 'QUOTED-PRINTABLE':
            text = quopri.decodestring(text)
    
        if part.media == 'TEXT' and part.media_subtype != 'HTML':
            # The HTML should have a meta tag with the correct charset encoding
            try:
                return unicode(text, part.charset())
            except UnicodeDecodeError:
                # Some times the messages have the wrong encoding, for instance
                # PHPMailer sends a text/plain with charset utf-8 but the actual 
                # contents are iso-8859-1. Here we can try to guess the encoding
                # on a case by case basis.
                try:
                    return unicode(text, 'iso-8859-1')
                except:
                    raise 
                    
        return text
        
    def fetch(self, query ):
        '''Returns the fetch response for the query
        '''
        return self._imap.fetch_smart(self.uid,query)[self.uid][query]
        
    def source(self):
        '''Returns the message source, untreated.
        '''
        return self.fetch('BODY[]')
        
    def part_header(self, part = None):
        '''Get a part header from the server.
        '''
        if part:
            query = 'BODY[%s.HEADER]'
        else:
            query = 'BODY[HEADER]'
            
        text = self._imap.fetch_smart(self.uid,query)[self.uid][query]
        
        return text
        
    def setFlags(self, flags):
        self.seen = SEEN in flags
        self.deleted = DELETED in flags
        self.answered = ANSWERED  in flags
        self.flagged = FLAGGED in flags
        self.draft = DRAFT in flags
        self.recent = RECENT in flags
        
    def __unicode__(self):
        return u'UID: %i' % self.uid
            
    def __str__(self):
        return self.__unicode__()
    
class Messages(object):
    def __init__(self, IMAP, folder ):
        object.__init__(self)
        self._imap = IMAP
        self.folder = folder
        self.search_criteria = 'ALL'
        self.sort_program = '(REVERSE DATE)'
        self._messages = None 
        
    def change_search(self, search_criteria):
        self.search_criteria = search_criteria
        self._messages = self._getMessageIDs()
        return self
        
    def change_sort(self, sort_program):
        self.sort_program = sort_program
        self._messages = self._getMessageIDs()
        return self
        
    def _getMessageIDs(self):
        '''Fetch the message list from the server.
        '''
        return self._imap.sort_smart(self.sort_program, 
            'UTF-8', self.search_criteria)
            
    def len(self):
        '''Returns the number of messages on the folder.
        '''
        if not self._messages:
            self._messages = self._getMessageIDs()
        return len(self._messages)
        
    def _getHeaders(self, i=0, j=-1):
        '''Extracts the messages header information.
        '''
        if not self._messages:
            self._messages = self._getMessageIDs()
            
        if len(self._messages) == 0:
            return
            
        if j==-1:
            msg_list = self._messages[i:]
        elif i == j:
            msg_list =  self._messages[i]
        else:
            msg_list = self._messages[i:j]
         
        self._info = self._imap.fetch_smart(msg_list, 'ALL' )

    def __getitem__(self, message):
        '''Returns a single message. It fetches it from the server.
        '''
        if not self._messages:
            self._messages = self._getMessageIDs()
            
        message = int(message)

        if message in self._messages:
            try:
                return Message(self._imap, self.folder, 
                    message, self._info[message])
            except AttributeError:
                msg_index = list(self._messages).index(message)
                self._getHeaders(msg_index,msg_index)
                
                return Message(self._imap, self.folder, 
                    message,self._info[message])
        else:
            raise KeyError, 'Unknown message %s on IMAP Folder' % (
                message)
        
    def __iter__(self):
        '''Iteract through all the messages
        '''
        self._getHeaders()
        for message in self._messages:
            yield self.__getitem__(message)
            
    def __getslice__(self, i, j):
        '''Iteract throgh a slice of messages
        '''
        self._getHeaders(i,j)
        for message in self._messages[i:j]:
            yield self.__getitem__(message)
