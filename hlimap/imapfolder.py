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

'''imapfolder module, this is a part of the hlimap IMAP Lib

Folder handling classes. Everything related to folders is handled here.
'''

# Imports
from utils import *
from imapmessage import *

Debug = 5
# Classes

class Flags(object):
    def __init__(self, flag_list, permanent_flags=[r'\*']):
        self.flag_list = flag_list
        self.permanent_flags = permanent_flags
        
    def permanentOK(self, flag):
        '''Checks if the flag can be changed permanently.
        
        (the session must be read/write)
        '''
        flag = flag.upper()
        if flag == r'\RECENT':
            # This flag can't be changed
            return False
        if r'\*' in self.permanent_flags:
            return True
        elif flag in self.permanent_flags:
            return True
        return False
        
    def flagOK(self, flag):
        '''Checks if flag  is applicable.
        '''
        flag = flag.upper()
        if flag in self.flag_list:
            return True
            
    def keywords(self):
        '''Iterator through flags that don't begin with '\'
        '''
        for flag in self.flag_list:
            if flag[0] != '\\':
                yield flag
        

class Folder(object):
    def __init__(self, IMAP, folder, folder_list):
        object.__init__(self)
        self._imap = IMAP
        # When we use imaplib to get the folder names we get 
        # a str, however, if we invoque this with a unicode 
        # string we will get an exception when we try to
        # convert the utf-7 string in __unicode__. Because of this
        # we force the convertion.
        self.folder_list = folder_list
        self.folder = folder
        self.flags = None
        self.__messages = None
        self.setStatus()
     
    def append( self, message ):
        '''Appends a message to this folder
        '''
        self._imap.append( self.folder.native(), message, '(\Seen)' )
    
    def url(self):
        return self.folder.url()
        
    def unicode(self):
        return self.__unicode__()
  
    def __unicode__(self):
        try:
            return unicode(self.folder.get_str('.').replace('+','+-').replace('&','+'),'utf-7')
        except UnicodeDecodeError:
            return unicode(self.folder.get_str('.').replace('+','+-').replace('&','+'),'utf-8')
        # The inverse is: u'ã'.encode('utf-7').replace('+','&') Returns: '&AOM-'
                
    def __str__(self):
        return self.__unicode__().encode('utf-8')
     
    def _getMessages(self):
        if not self.__messages:
            self.__messages = Messages(self._imap, self.folder )
        return self.__messages
    messages = property(_getMessages)
        
    def select(self):
        if self.folder_list.isSelected():
            self._imap.close()
        result = self._imap.select(self.folder.native())
        self.folder_list.setSelected( self.folder.native() )
        
        self.flags = Flags(result['FLAGS'], result['PERMANENTFLAGS'])
        
        self.status['MESSAGES'] = result['EXISTS'] 
        # What's the diff between MESSAGES from the STATUS command and EXISTS 
        # from the optional responses of the SELECT command? They sure return
        # different values...
        try:
            self.status['RECENT'] = result['RECENT']
        except:
            self.status['RECENT'] = 0
        try:
            self.status['UNSEEN'] = result['UNSEEN']
        except:
            self.status['UNSEEN'] = 0
           
        return self
        
    def setStatus(self):
        if self.folder.noselect():
            self.status = {}
            return
        else:
            self.status = self._imap.status(self.folder.native(),
                '(MESSAGES RECENT UIDNEXT UIDVALIDITY UNSEEN)')
        
        if not self.status:
            raise HLError('Couldn\'t get the status for folder'
                ' %s' % self.folder)
                
    def total(self):
        '''Total number o messages on the mailbox
        '''
        return self.status['MESSAGES']
        
    def recent(self):
        '''Number of recent messages on the mailbox
        '''
        return self.status['RECENT']
        
    def unseen(self):
        '''Number of unseen messages on the mailbox
        '''
        return self.status['UNSEEN']

class Folders(object):
    '''Manages the folders tree. This is essencialy a container class for the
    folder list. 
    
    We can get a folder in one of two ways, either we reference the folder just
    as if this class was a dictionary:
    
    >>> M = ImapServer('example.com')
    >>> M.login('example user','example pass')
    >>> folder = M.folders['INBOX']
    
    Or we can iteract through the folders:
    
    >>> M = ImapServer('example.com')
    >>> M.login('example user','example pass')
    >>> for folder in folders:
    ...     print folder
    INBOX.Teste UTF-8 çãáàâ
    INBOX.Trash
    INBOX.Tretas Maximas
    INBOX
    
    The main diference is that in the first case we issue a list/lsub IMAP 
    command to get ONLY the folder data. On the second case the list command 
    used fetches all the folders that match the pattern provided on the 
    constructor.
    
    The list/lsub commands are fairly fast, however, since we issue a status 
    imap command for each folder, this can get very slow. Thus the two methods
    to get a folder.
    '''
    def __init__(self, IMAP, directory = '', subscribed = True, pattern = '*'):
        object.__init__(self)
        self._imap = IMAP
        self.sstatus = IMAP.sstatus
        self.directory = directory
        self.subscribed = subscribed
        self.pattern = pattern
        self._folders = None
        self.selected = '' # Selected folder name
    
    def _getFolders(self):
        if self.subscribed:
            result = self._imap.lsub(self.directory, self.pattern)
        else:
            result = self._imap.list(self.reference, self.pattern)

        self._folders = result
       
    def __getitem__(self, folder):
        if isinstance(folder, str) or isinstance(folder, unicode):
            # Directly accessing a folder, retrieve folder info
            folder = base64.urlsafe_b64decode(str(folder))
            folder = self._imap.list(folder, '%')[0]
            
        return Folder(self._imap, folder, self)

    def __iter__(self):
        if not self._folders:
            self._getFolders()
            
        for folder in self._folders:
            yield self.__getitem__( folder )
        
    def refresh(self):
        self._getFolders()
        
    def setSelected( self, folder ):
        self.selected = folder
        
    def isSelected(self):
        return bool(self.selected)
