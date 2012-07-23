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

import uno
import unohelper

from com.sun.star.awt import XActionListener, \
    XContainerWindowEventHandler
from incsearch.tools import get_config, ServiceInfo
from incsearch import \
    CONFIG_NODE_SETTINGS, NAME_DICTIONARY


class OptionsPageHandler(unohelper.Base, 
        XContainerWindowEventHandler, ServiceInfo):
    """ Option page implementation for incremental search. """
    
    from incsearch import OPTION_IMPLE_NAME as IMPLE_NAME
    SERVICE_NAMES = (IMPLE_NAME,)
    
    class ButtonListener(unohelper.Base, XActionListener):
        def __init__(self, act):
            self.act = act
        
        def disposing(self, ev): pass
        
        def actionPerformed(self, ev):
            self.act.button_pushed(ev.Source)
    
    def __init__(self, ctx, args):
        self.ctx = ctx
        self.dialog = None
        #self.res = get_current_resource(ctx, RES_DIR, RES_FILE)
    
    #def _(self, name):
    #    return self.res.get(name, name)
    
    # XContainerWindowEventHandler
    def getSupportedMethodNames(self):
        return ("external_event", )
    
    def callHandlerMethod(self, window, ev, name):
        if name == "external_event":
            self.handle(window, ev)
    
    def handle(self, dialog, ev):
        self.dialog = dialog
        if ev == "ok":
            self.confirm()
        elif ev == "back":
            self.init()
        elif ev == "initialize":
            self.init(True)
        return True
    
    def get(self, name):
        return self.dialog.getControl(name)
    
    def get_text(self, name):
        return self.get(name).getModel().Text
    
    def set_text(self, name, text):
        if text is None:
            text = ""
        self.get(name).getModel().Text = text
    
    def set_state(self, name, state):
        if state is None:
            state = False
        self.get(name).getModel().State = {True: 1, False: 0}[state]
    
    def get_state(self, name):
        return self.get(name).getModel().State
    
    def translate_labels(self):
        _ = self._
        dialog_model = self.dialog.getModel()
        dialog_model.Title = _(dialog_model.Title)
        for control in self.dialog.getControls():
            model = control.getModel()
            if hasattr(model, "Label"):
                model.Label = _(model.Label)
    
    def init(self, first_time=False):
        try:
            config = get_config(self.ctx, CONFIG_NODE_SETTINGS)
            cp = config.getPropertyValue
            self.set_text("edit_dictionary", cp(NAME_DICTIONARY))
            #self.translate_labels()
            if first_time:
                self.get("btn_dictionary").addActionListener(self.ButtonListener(self))
        except Exception, e:
            print(e)
            import traceback
            traceback.print_exc()
    
    def confirm(self):
        config = get_config(self.ctx, CONFIG_NODE_SETTINGS, True)
        cs = config.setPropertyValue
        cs(NAME_DICTIONARY, self.get_text("edit_dictionary"))
        config.commitChanges()
    
    def button_pushed(self, control):
        result = self.choose_file()
        if result:
            name = None
            if control == self.get("btn_dictionary"):
                name = "edit_dictionary"
            if name:
                self.set_text(name, result)
    
    def choose_file(self):
        fp = self.ctx.getServiceManager().createInstanceWithContext(
            "com.sun.star.ui.dialogs.FilePicker", self.ctx)
        fp.initialize((0,))
        if fp.execute():
            return fp.getFiles()[0]
        return None

