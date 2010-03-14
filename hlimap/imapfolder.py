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
# $Id: imapfolder.py 20 2010-01-15 20:44:48Z hguerreiro $
#
from imapmessage import MessageList
from imaplib2.parselist import Mailbox
import base64

class DupError(Exception): pass
class NoSuchFolder(Exception): pass
class NoFolderListError(Exception): pass

class FolderTree(object):
    def __init__(self, server ):
        '''Initializes the folder tree.
        '''
        self._imap = server._imap
        self.server = server
        self.dl = None
        self.folder_dict = {}
        self.root_folder = []
        self.selected = None

    def refresh_folders( self, subscribed=True ):
        # It's very fast to retrieve the folder listing, so we just
        # query the server for all the folders.
        if subscribed:
            flat_list = self._imap.lsub("", "*")
        else:
            flat_list = self._imap.list("", "*")

        if not flat_list:
            raise NoFolderListError('No folders found')

        self.dl = flat_list[0].delimiter

        for mailbox in flat_list:
            self.add_folder( mailbox.parts, subscribed,
                             noselect = mailbox.noselect() )

        self.sort()

    def add_folder( self, parts, subscribed, child = None, noselect = False ):
        path = self.dl.join( parts )
        if not self.folder_dict.has_key(path):
            self.folder_dict[ path ] = { 'data' : Folder(self.server, self, parts,
                                                         subscribed, noselect),
                                         'children': [] }
            if len(parts) == 1:
                self.root_folder.append( path )

        if child:
            if child not in self.folder_dict[ path ]['children']:
                self.folder_dict[ path ]['children'].append( child )

        parent_parts = parts[:-1]

        if parent_parts:
            parent_path = self.dl.join( parent_parts )
            if not self.folder_dict.has_key( parent_path ):
                self.add_folder( parent_parts, False, child = path,
                    noselect = True )
            else:
                self.add_folder( parent_parts, subscribed, child = path )


    # Set folder properties
    def set_properties(self, expand_list,  special_folders):
        for folder_name in expand_list:
            if self.folder_dict.has_key( folder_name ):
                self.folder_dict[folder_name]['data'].set_expand(True)

        for folder_name in special_folders:
            if self.folder_dict.has_key( folder_name ):
                self.folder_dict[folder_name]['data'].special = True

    def sort(self, folder_list = None):
        '''Sorts the folders.
        '''
        def compare( name1, name2 ):
            spc1 = self.folder_dict[name1]['data'].special

            spc2 = self.folder_dict[name2]['data'].special

            if spc1 and not spc2:
                return -1
            elif not spc1 and spc2:
                return 1
            else:
                return cmp( name1, name2 )

        if not folder_list:
            folder_list = self.root_folder

        folder_list.sort(compare)

        for folder_name in folder_list:
            children = self.folder_dict[folder_name]['children']
            if children:
                self.sort( children )


    def refresh_status(self):
        for folder in self.iter_all():
            folder.refresh_status()

    # Iterators

    def iter_all(self, folder_list = None):
        '''Iteract through all the folders
        '''
        if folder_list == None:
            folder_list = self.root_folder

        for folder_name in folder_list:
            yield self.folder_dict[folder_name]['data']
            # iteract children
            children = self.folder_dict[folder_name]['children']
            for child in self.iter_all( children ):
                yield child

    def iter_expand(self, folder_list = None):
        '''Iteract through the folders that have the folder.expanded flag_list
        set.
        '''
        if folder_list == None:
            folder_list = self.root_folder

        for folder_name in folder_list:
            folder = self.folder_dict[folder_name]['data']
            yield folder
            # iteract children
            if folder.expanded:
                children = self.folder_dict[folder_name]['children']
                for child in self.iter_expand( children ):
                    yield child

    # Folder operations
    def get_folder(self, path):
        if not self.folder_dict.has_key(path):
            try:
                mailbox = self._imap.lsub("", path)[0]
                self.dl = mailbox.delimiter
            except IndexError:
                raise NoSuchFolder(path)
            self.add_folder( mailbox.parts, True,
                child = None, noselect = mailbox.noselect() )

        folder = self.folder_dict[path]['data']

        if self.selected and self._imap.has_capability('UNSELECT'):
            self._imap.unselect()
            self.selected = None
        self.selected = folder.select()

        return folder


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
    def __init__(self, server, tree, parts, subscribed=True,
        noselect = False):
        self._imap = server._imap
        self.server = server
        self.tree = tree
        self.server = server

        # Load the mailbox
        self.name = parts[-1]
        self.path = tree.dl.join( parts )
        if len(parts) > 1:
            self.parent = tree.dl.join( parts[:-1] )
        else:
            self.parent = None
        self.parts = parts

        # Tree behavior
        self.expanded = False
        self.special = False
        self.noselect = noselect
        self.subscribed = subscribed

        # Status
        self.status = {}
        self.flags = None

        # Messages
        self.__message_list = None

    # Attributes
    def haschildren(self):
        return bool(self.tree.folder_dict[self.path]['children'])
    has_children = property( haschildren )

    def set_expand(self, value):
        self.expanded = value
        #if value:
            ## If the folder is to be expanded then all parent folders
            ## should also be expanded
            #if self.parent:
                #self.tree.folder_dict[self.parent]['data'].set_expand(True)

    # Mailbox statistics
    def refresh_status(self):
        if not self.noselect:
            self.status = self._imap.status(self.path,
                '(MESSAGES RECENT UIDNEXT UIDVALIDITY UNSEEN)')
        else:
            self.status = {}

    def get_status(self, prop):
        if not self.status:
            self.refresh_status()
        return self.status[prop]

    def messages(self):
        return self.get_status('MESSAGES')
    total = messages
    def recent(self):
        return self.get_status('RECENT')
    def uid_next(self):
        return self.get_status('UIDNEXT')
    def uid_validity(self):
        return self.get_status('UIDVALIDITY')
    def unseen(self):
        return self.get_status('UNSEEN')

    # Mailbox name
    def level(self):
        return len(self.parts)-1

    def last_level(self):
        return self.name

    def native(self):
        '''Return the mailbox in raw format using the delimiter
        understood by the server.
        '''
        return self.path

    def url(self):
        '''Return the folder name on a url safe way
        '''
        return base64.urlsafe_b64encode(self.path)

    def unicode_name(self):
        return self.__unicode__()

    # Messages
    def append( self, message ):
        '''Appends a message to this folder
        '''
        self._imap.append( self.path, message, '(\Seen)' )

    # Folder operations:
    def select(self):
        def get_status( result, key ):
            try:
                return result[key]
            except KeyError:
                return 0

        result = self._imap.select( self.path )

        self.flags = Flags(result['FLAGS'], result['PERMANENTFLAGS'])

        self.status['MESSAGES'] = result['EXISTS']
        # What's the diff between MESSAGES from the STATUS command and EXISTS
        # from the optional responses of the SELECT command? They sure return
        # different values...

        self.status['RECENT'] = get_status(result, 'RECENT')
        self.status['UNSEEN'] = get_status(result, 'UNSEEN')
        if self._imap.has_capability('UIDPLUS'):
            self.status['UIDNEXT'] = get_status(result, 'UIDNEXT')
            self.status['UIDVALIDITY'] = get_status(result, 'UIDVALIDITY')

        return self

    def expunge(self):
        self._imap.expunge()
        self.__message_list = None

    def set_flags(self, message_list, *args ):
        return self._imap.store_smart(message_list, '+FLAGS.SILENT', args)

    def reset_flags(self, message_list, *args ):
        return self._imap.store_smart(message_list, '-FLAGS.SILENT', args)

    # Message list management
    def _get_message_list(self):
        if not self.__message_list:
            self.__message_list = MessageList( self.server, self )
        return self.__message_list
    message_list = property(_get_message_list)

    def have_messages(self):
        '''Are there any messages on the folder?'''
        return self.message_list.have_messages()

    def refresh_messages(self):
        self.message_list.refresh_messages()

    def paginator(self):
        return self.message_list.paginator

    # Special methods
    def __unicode__(self):
        mailbox = self.name
        try:
            return unicode(mailbox.replace('+','+-').replace('&','+'),'utf-7')
        except UnicodeDecodeError:
            return unicode(mailbox.replace('+','+-').replace('&','+'),'utf-8')

    def __repr__(self):
        return '<Folder instance "%s">' % (self.name)

    def __getitem__(self, message_id ):
        '''Returns Message Object'''
        if type(message_id) != int:
            raise TypeError('The message id must ben an integer.')

        return self.message_list.get_message( message_id )

    def __iter__(self):
        return self.message_list.msg_iter_page()





