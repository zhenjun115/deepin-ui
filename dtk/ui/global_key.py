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

from Xlib import X
from Xlib.display import Display
from keymap import parse_keyevent_name
import gtk
import threading

class GlobalKey(threading.Thread):

    def __init__(self):
        super(GlobalKey, self).__init__()
        self.daemon = True
        self.display = Display()
        self.root = self.display.screen().root
        self._binding_map = {}
        self.stop = False
        self.running = True

        self.known_modifiers_mask = 0
        gdk_modifiers = (gtk.gdk.CONTROL_MASK, gtk.gdk.SHIFT_MASK, gtk.gdk.MOD1_MASK,
                         gtk.gdk.MOD2_MASK, gtk.gdk.MOD3_MASK, gtk.gdk.MOD4_MASK, gtk.gdk.MOD5_MASK,
                         gtk.gdk.SUPER_MASK, gtk.gdk.HYPER_MASK)
        for mod in gdk_modifiers:
            self.known_modifiers_mask |= mod

    def bind(self, binding_string, action):
        keyval, modifiers = parse_keyevent_name(binding_string)
        keycode = gtk.gdk.keymap_get_default().get_entries_for_keyval(keyval)[0][0]
        self._binding_map[(keycode, modifiers)] = action
        self.regrab()
        
    def unbind(self, binding_string):
        keyval, modifiers = parse_keyevent_name(binding_string)
        keycode = gtk.gdk.keymap_get_default().get_entries_for_keyval(keyval)[0][0]
        if self._binding_map.has_key((keycode, modifiers)):
            del self._binding_map[(keycode, modifiers)]
            self.regrab()

    def grab(self):
        for (keycode, modifiers) in self._binding_map.keys():
            try:
                self.root.grab_key(keycode, int(modifiers), True, X.GrabModeAsync, X.GrabModeSync)
            except Exception, e:
                print e

    def ungrab(self):
        for (keycode, modifiers) in self._binding_map.keys():
            try:
                self.root.ungrab_key(keycode, modifiers, self.root)
            except Exception, e:
                print e

    def regrab(self):
        self.ungrab()
        self.grab()

    def run(self):
        wait_for_release = False
        while not self.stop:
            event = self.display.next_event()
            if self.running:
                if event.type == X.KeyPress and not wait_for_release:
                    keycode = event.detail
                    modifiers = event.state & self.known_modifiers_mask
                    try:
                        action = self._binding_map[(keycode, modifiers)]
                    except KeyError:
                        self.display.allow_events(X.ReplayKeyboard, event.time)
                    else:
                        wait_for_release = True
                        self.display.allow_events(X.AsyncKeyboard, event.time)
                        self._upcoming_action = (keycode, modifiers, action)
                
                elif event.type == X.KeyRelease and wait_for_release and event.detail == self._upcoming_action[0]:
                    wait_for_release = False
                    action = self._upcoming_action[2]
                    del self._upcoming_action
                    action()
                    self.display.allow_events(X.AsyncKeyboard, event.time)
                
                else:
                    self.display.allow_events(X.ReplayKeyboard, event.time)

    def stop(self):
        self.stop = True
        self.ungrab()
        self.display.close()
        
if __name__ == "__main__":
    gtk.gdk.threads_init()
    
    def t(*args, **kwargs):
        print 'Called!'
    manager = GlobalKey()
    # manager.bind('Ctrl + Alt + Shift + s', t)
    manager.bind('Ctrl + Alt + S', t)
    manager.start()

    gtk.main()
