#  Copyright 2012 Tsutomu Uchino
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import unohelper

from com.sun.star.frame import \
    XStatusListener, XToolbarController, XSubToolbarController
from com.sun.star.util import XUpdatable

import incsearch.tools

class ToolbarControllerBase(unohelper.Base, 
    XStatusListener, XToolbarController, 
    XUpdatable, incsearch.tools.ServiceBase, XSubToolbarController):
    """ Base class for toolbar controller. """
    
    def __init__(self, ctx, args):
        self.ctx = ctx
        self.frame = None
        self.command = None
        self.initialize(args)
    
    # XInitialization
    def initialize(self, args):
        for arg in args:
            name = arg.Name
            if name == "Frame":
                self.frame = arg.Value
            elif name == "CommandURL":
                self.command = arg.Value
    
    # XStatusListener
    def statusChanged(self, state): pass
    
    # XUpdatable
    def update(self): pass
    
    # XToolbarController
    def execute(self, mod): pass
    def click(self): pass
    def doubleClick(self): pass
    def createPopupWindow(self):
        return None
    
    def createItemWindow(self, parent):
        self.parent = parent
    
    # XSubToolbarController
    def opensSubToolbar(self):
        return False
    def getSubToolbarName(self): return ""
    def functionSelected(self, command): pass
    def updateImage(self): pass

from com.sun.star.awt.WindowClass import SIMPLE as WC_SIMPLE
from com.sun.star.awt.WindowAttribute import \
    SHOW as WA_SHOW#, BORDER as WA_BORDER, 

from com.sun.star.awt import Rectangle, WindowDescriptor

import incsearch

class IncrementalSearchToolbarController(ToolbarControllerBase):
    """ Toolbar controller for search toolbar. """
    from incsearch import IMPLE_NAME, SERVICE_NAMES
    
    def createItemWindow(self, parent):
        box = None
        try:
            # bg color is not appear if BORDER is specified
            box = create_window(parent.getToolkit(), parent, 
                    WC_SIMPLE, "edit", WA_SHOW, 
                    5, 2, 150, 23)
            incsearch.frames.add_item(self, box)
        except Exception, e:
            print(e)
        return box


def create_window(toolkit, parent, wtype, service, attrs, x, y, width, height):
    """ Create new window. """
    return toolkit.createWindow(
        WindowDescriptor(
            wtype, service, 
            parent, -1, 
            Rectangle(x, y, width, height), attrs))

