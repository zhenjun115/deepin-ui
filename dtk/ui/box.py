#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang Yong
# 
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
#             Zhai Xiang <zhaixiang@linuxdeepin.com>
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

from draw import draw_pixbuf, propagate_expose, draw_vlinear, cairo_state, draw_line
from theme import ui_theme
from skin_config import skin_config
from utils import get_window_shadow_size
import gobject
import gtk

class EventBox(gtk.EventBox):
    '''
    Event box, not like Gtk.EventBox, it don't show visible window default.
    '''
	
    def __init__(self):
        '''
        Initialize the EventBox class.
        '''
        gtk.EventBox.__init__(self)
        self.set_visible_window(False)
        
class ImageBox(gtk.EventBox):
    '''
    ImageBox.
    
    @undocumented: expose_image_box
    '''
	
    def __init__(self, image_dpixbuf):
        '''
        Initialize the ImageBox class.

        @param image_dpixbuf: Image dynamic pixbuf.
        '''
        # Init.
        gtk.EventBox.__init__(self)
        self.set_visible_window(False)
        self.image_dpixbuf = image_dpixbuf
        
        # Set size.
        pixbuf = self.image_dpixbuf.get_pixbuf()
        self.set_size_request(pixbuf.get_width(), pixbuf.get_height())
        
        # Connect expose signal.
        self.connect("expose-event", self.expose_image_box)
        
    def expose_image_box(self, widget, event):
        '''
        Callback for `expose-event` signal.

        @param widget: Gtk.Widget instance.
        @param event: Expose event.
        '''
        # Init.
        cr = widget.window.cairo_create()
        rect = widget.allocation
        pixbuf = self.image_dpixbuf.get_pixbuf()
        
        # Draw.
        draw_pixbuf(cr, pixbuf, rect.x, rect.y)
        
        # Propagate expose.
        propagate_expose(widget, event)
    
        return True
    
gobject.type_register(ImageBox)

class BackgroundBox(gtk.VBox):
    '''
    BackgroundBox is container for clip background.
    
    @undocumented: expose_background_box
    '''
	
    def __init__(self):
        '''
        Initialize the BackgroundBox class.
        '''
        # Init.
        gtk.VBox.__init__(self)
        self.set_can_focus(True)
        
        self.connect("expose-event", self.expose_background_box)
        
    def draw_mask(self, cr, x, y, w, h):
        '''
        Mask render function.
        
        @param cr: Cairo context.
        @param x: X coordinate of draw area.
        @param y: Y coordinate of draw area.
        @param w: Width of draw area.
        @param h: Height of draw area.
        '''
        draw_vlinear(cr, x, y, w, h,
                     ui_theme.get_shadow_color("linear_background").get_color_info()
                     )
        
    def expose_background_box(self, widget, event):
        '''
        Callback for `expose-event` signal.

        @param widget: BackgroundBox self.
        @param event: Expose event.        
        @return: Always return False.        
        '''
        cr = widget.window.cairo_create()
        rect = widget.allocation
        toplevel = widget.get_toplevel()
        coordinate = widget.translate_coordinates(toplevel, rect.x, rect.y)
        (offset_x, offset_y) = coordinate
        
        with cairo_state(cr):
            cr.rectangle(rect.x, rect.y, rect.width, rect.height)
            cr.clip()
            
            (shadow_x, shadow_y) = get_window_shadow_size(toplevel)
            skin_config.render_background(cr, widget, shadow_x, shadow_y)
            
        self.draw_mask(cr, rect.x, rect.y, rect.width, rect.height)    

        return False
        
gobject.type_register(BackgroundBox)

'''
TODO: Resizable can be drag toward downward
'''
class ResizableEventBox(gtk.EventBox):
    def __init__(self, padding_x, width, height):
        gtk.EventBox.__init__(self)
        self.padding_x = padding_x
        self.padding_y = 20
        self.width = width
        self.height = height
        self.bottom_right_corner_pixbuf = ui_theme.get_pixbuf("box/bottom_right_corner.png")
        self.button_pressed = False
        self.connect("button-press-event", self.m_button_press)
        self.connect("button-release-event", self.m_button_release)
        self.connect("motion-notify-event", self.m_motion_notify)
        self.connect("expose-event", self.m_expose)

    def m_button_press(self, widget, event):
        self.button_pressed = True

    def m_button_release(self, widget, event):
        self.button_pressed = False

    def m_motion_notify(self, widget, event):
        self.height = event.y - self.padding_y
        cursor_changable = False
        
        '''
        FIXME: change cursor style wrong
        if self.height - event.y < 20:
            cursor_changable = True
            self.get_window().set_cursor(gtk.gdk.Cursor(gtk.gdk.BOTTOM_SIDE))
        else:
            cursor_changable = False
            self.get_window().set_cursor(gtk.gdk.Cursor(gtk.gdk.ARROW))
        '''
        if self.button_pressed:
            # redraw the widget
            self.window.invalidate_rect(self.allocation, True)

    def m_expose(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        x, y = rect.x, rect.y
        
        with cairo_state(cr):
            '''
            stroke
            '''
            cr.set_source_rgba(153, 153, 153, 1.0)
            draw_line(cr, 
                      x + self.padding_x, 
                      y, 
                      x + self.padding_x + self.width, 
                      y)
            draw_line(cr, 
                      x + self.padding_x + self.width, 
                      y, 
                      x + self.padding_x + self.width, 
                      y + self.height)
            draw_line(cr, 
                      x + self.padding_x + self.width, 
                      y + self.height, 
                      x + self.padding_x, 
                      y + self.height)
            draw_line(cr, 
                      x + self.padding_x, 
                      y + self.height, 
                      x + self.padding_x, 
                      y)

            draw_pixbuf(cr, 
                        self.bottom_right_corner_pixbuf.get_pixbuf(), 
                        x + self.width - self.padding_x, 
                        y + self.height - self.padding_y)

        propagate_expose(widget, event)

        return True

gobject.type_register(ResizableEventBox)

class ResizableBox(gtk.VBox):
    def __init__(self, padding_x, width):
        gtk.VBox.__init__(self)
        self.padding_x = padding_x
        self.width = width
        self.height = 200
        self.align = gtk.Alignment()
        self.align.set(0.5, 0.5, 1.0, 1.0)
        self.resizable_eventbox = ResizableEventBox(self.padding_x, self.width, self.height)
        self.pack_start(self.align)
        self.align.add(self.resizable_eventbox)
        self.align.connect("expose-event", self.m_expose)

    def m_expose(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        x, y = rect.x, rect.y

        propagate_expose(widget, event)

        return True

gobject.type_register(ResizableBox)
