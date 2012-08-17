#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang Yong
# 
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from new_treeview import TreeItem
import gobject

class DirItem(TreeItem):
    '''
    Directory item.
    '''
	
    def __init__(self, directory_path):
        '''
        Initialize DirItem class.
        '''
        TreeItem.__init__(self)
        
gobject.type_register(DirItem)

class FileItem(TreeItem):
    '''
    File item.
    '''
	
    def __init__(self, directory_path):
        '''
        Initialize FileItem class.
        '''
        TreeItem.__init__(self)
        
gobject.type_register(DirItem)
