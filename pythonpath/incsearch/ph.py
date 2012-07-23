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

import incsearch
import incsearch.tools

from com.sun.star.frame import XDispatchProvider

class IncrementalSearchProtocolHandler(unohelper.Base, 
    XDispatchProvider, incsearch.tools.ServiceBase):
    """ Protocol handler for incremental search command. """
    
    from incsearch import PH_IMPLE_NAME as IMPLE_NAME, \
        PH_SERVICE_NAMES as SERVICE_NAMES, PH_PROTOCOL
    
    def __init__(self, ctx, args):
        self.ctx = ctx
        self.frame = None
        self.command = None
        self.initialize(args)
    
    # XInitialization
    def initialize(self, args):
        if len(args) > 0:
            self.frame = args[0]
    
    def queryDispatches(self, descs): pass
    def queryDispatch(self, url, name, flags):
        if url.Protocol == self.PH_PROTOCOL:
            if url.Path in ("Focus", "Direction"):
                self.command = url.Complete
                incsearch.frames.add_item(self, None)
                return incsearch.frames.get_item(self, self.command)
        return None

