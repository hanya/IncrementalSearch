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

class FrameKeeper(object):
    """ Manages frames. """
    def __init__(self, class_name):
        self.frames = []
        self._class_name = class_name
        self.klass = None
    
    def count(self):
        """ Returns number of frames kept. """
        return len(self.frames)
    
    def _find(self, value):
        """ Find frame index. """
        return self.frames.index(value.frame)
        """
        i = 0
        for frame in self.frames:
            if frame.frame == value.frame:
                return i
            i += 1
        raise KeyError()
        """
    def add(self, value):
        """ Add new frame. """
        try:
            self._find(value)
        except:
            self.frames.append(value)
    
    def remove(self, value):
        """ Remove existing frame. """
        try:
            n = self._find(value)
            self.frames.pop(n)
        except:
            pass
    
    def get(self, value):
        """ Get frame. """
        try:
            n = self._find(value)
            return self.frames[n]
        except:
            return None
    
    def add_item(self, item, ctrl):
        """ Add item to a frame. """
        frame = self.get(item)
        if frame is None:
            if self.klass is None:
                self.load_class()
            frame = self.klass(item.ctx, item.frame)
            self.add(frame)
        frame.set(item, ctrl)
    
    def get_item(self, item, command):
        """ Get item from a frame. """
        frame = self.get(item)
        if not frame is None:
            return frame.get(item, command)
    
    def load_class(self):
        """ Load class by name. """
        try:
            parts = self._class_name.split(".")
            mod = __import__(".".join(parts[0:-1]))
            for part in parts[1:-1]:
                mod = getattr(mod, part)
            self.klass = getattr(mod, parts[-1])
        except Exception,e:
            print(e)

