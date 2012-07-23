# -*- encoding: utf-8 -*-
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
import traceback

from com.sun.star.awt import XKeyListener, XTextListener, Selection
from com.sun.star.awt.Key import \
    RETURN as K_RETURN, ESCAPE as K_ESCAPE, \
    B as K_B, E as K_E, D as K_D, H as K_H, M as K_M, R as K_R, T as K_T
from com.sun.star.awt.KeyModifier import SHIFT, MOD1
from com.sun.star.frame import XDispatch, \
    FeatureStateEvent, ControlCommand
from com.sun.star.lang import XEventListener
from com.sun.star.beans import NamedValue, PropertyValue


class ListenerBase(unohelper.Base):
    """ Base class for listeners. """
    def __init__(self, act):
        self.act = act
    
    def disposing(self, ev): pass

class DocumentEventListener(ListenerBase, XEventListener):
    """ For document closing. """
    def disposing(self, ev):
        self.act.dispose()
        self.act = None


class Dispatcher(ListenerBase, XDispatch):
    """ Execute dispatch. """
    def get_mod(self, args):
        for arg in args:
            if arg.Name == "KeyModifier":
                return arg.Value
        return 0
    
    def dispatch(self, url, args):
        self.act.focus_to_box()
        if self.get_mod(args):
            self.act.show_help()
    
    def addStatusListener(self, control, url):
        try:
            self.act.add_status_listener(url.Path, control)
            self.act.init_state(url.Path)
        except Exception, e:
            print(e)
    
    def removeStatusListener(self, control, url):
        self.act.remove_status_listener(url.Path, control)


class StatusListenerContainer(object):
    """ Keeps status listeners. """
    def __init__(self):
        self._status_listeners = {}
    
    def add_status_listener(self, command, control):
        listeners = None
        try:
            listeners = self._status_listeners[command]
        except:
            listeners = []
            self._status_listeners[command] = listeners
        listeners.append(control)
    
    def remove_status_listener(self, command, control):
        try:
            listeners = self._status_listeners[command]
            while True:
                listeners.remove(control)
        except:
            pass
    
    def change_event(self, command, ev):
        try:
            listeners = self._status_listeners[command]
            for listener in listeners:
                listener.statusChanged(ev)
        except:
            pass


class TextListener(ListenerBase, XTextListener):
    """ Checks text changes. """
    def textChanged(self, ev):
        try:
            self.act.start_search()
        except Exception, e:
            print(e)


class KeyListener(ListenerBase, XKeyListener):
    """ Listener for key. """
    def keyReleased(self, ev): pass
    def keyPressed(self, ev):
        code = ev.KeyCode
        if code == K_ESCAPE:
            self.act.set_text("")
        elif code == K_RETURN:
            self.act.start_search(True, not not (ev.Modifiers & SHIFT))
        elif ev.Modifiers & MOD1:
            if code == K_D:
                self.act.focus_to_doc()
            elif code == K_M:
                self.act.enable_migemo(ev.Modifiers & SHIFT)
            elif code == K_B:
                self.act.enable_backward(ev.Modifiers & SHIFT)
            elif code == K_E:
                self.act.enable_case_sensitive(ev.Modifiers & SHIFT)
            elif code == K_R:
                self.act.enable_regex(ev.Modifiers & SHIFT)
            else:
                try:
                    if code == K_H:
                        self.act.change_search_direction()
                    elif code == K_T:
                        self.act.change_search_type()
                except:
                    pass


from incsearch import PROTOCOL, PH_PROTOCOL, INC_PATH
import incsearch

class FrameKeeper(object):
    """ Keeps real frame. """
    def __init__(self, frame):
        self.frame = frame
    
    def __eq__(self, other):
        try:
            return self.frame == other
        except:
            return False
    
    def __ne__(self, other):
        try:
            return self.frame != other
        except:
            return True


def create_imple(ctx, frame):
    """ Create search imple according to the type of document. """
    id = frame.getController().getModel().getIdentifier()
    if id == "com.sun.star.text.TextDocument":
        return WriterSearch(ctx, frame)
    elif "com.sun.star.sheet.SpreadsheetDocument":
        return CalcSearch(ctx, frame)
    return None


class SearchImple(FrameKeeper, StatusListenerContainer):
    """ Base class for searching. """
    NOT_FOUND_BG_COLOR = 0xff6666
    NOT_FOUND_TEXT_COLOR = 0xffffff
    
    migemo = None
    
    HELP_TITLE = "Incremental Search"
    HELP_TEXT = """\
Input text: Incremental search
Enter: Search next
Shift + Enter: Search to opposit direction
Esc: Clear text
Ctrl + M: Migemo on/off, "Mi"
Ctrl + E: Case-sensitive on/off, "A"
Ctrl + R: Regular expression on/off, "Re"
Ctrl + B: Backward search on/off, "<"
 + Shift: Force function on
Ctrl + D: Return back to the document
Ctrl + G: Move into the search field (on the document)
"""
    HELP_TITLE_JA = u"インクリメンタル検索"
    HELP_TEXT_JA = u"""\
テキスト入力: インクリメンタル検索
Enter: 次を検索
Shift + Enter: 逆方向に検索
Esc: 入力欄をクリア
Ctrl + M: Migemo オン/オフ、"Mi"
Ctrl + E: 大文字小文字区別 オン/オフ、"A"
Ctrl + R: 正規表現 オン/オフ、"Re"
Ctrl + B: 逆順検索 オン/オフ、"<"
 + Shift: 機能をオン
Ctrl + D: ドキュメントにフォーカスを戻す
Ctrl + G: ドキュメント上から検索欄にフォーカス
"""
    
    def __init__(self, ctx, frame):
        FrameKeeper.__init__(self, frame)
        StatusListenerContainer.__init__(self)
        self.ctx = ctx
        self.box = None
        self.descriptor = None
        self.dispatcher = None
        
        self.NORMAL_BG_COLOR = 0xffffff
        self.NORMAL_TEXT_COLOR = 0
        
        self.migemo_found = False
        
        self.migemo_enabled = False
        self.regex_enabled = False
        self.backward = False
        self.case_sensitive = False
        
        self._set_listener()
        self._init_migemo()
        self._init_descriptor()
    
    def _init_migemo(self):
        """ Initialize PyMigemo. """
        if self.__class__.migemo is None:
            try:
                import pymigemo
                dict_path = self.get_dictionary_path()
                if dict_path:
                    self.__class__.migemo = pymigemo.Migemo(dict_path)
                    self.migemo_found = True
                    self.migemo_enabled = True
                    return
            except Exception, e:
                print("Error on loading PyMigemo: ")
                print(e)
            self.migemo_found = False
        else:
            self.migemo_found = True
            self.migemo_enabled = True
    
    def get_dictionary_path(self):
        """ Get path to CMigemo dict. """
        import incsearch.tools
        from incsearch import CONFIG_NODE_SETTINGS, NAME_DICTIONARY
        try:
            file_url = incsearch.tools.get_config_value(
                self.ctx, CONFIG_NODE_SETTINGS, NAME_DICTIONARY)
            return uno.fileUrlToSystemPath(file_url)
        except Exception, e:
            print(e)
            traceback.print_exc()
        return ""
    
    def _destroy(self):
        if self.__class__migemo:
            self.__class__.migemo = None
    
    def _init_descriptor(self):
        pass
    
    def set(self, item, obj):
        """ Set item. """
        if item.command == PROTOCOL + INC_PATH:
            self.box = obj
            self._box_setup(obj)
    
    def get(self, item, command):
        """ Get dispatcher for the command. """
        if command.startswith(PH_PROTOCOL):
            path = command[len(PH_PROTOCOL):]
            if path == "Focus" or path == "Direction":
                if self.dispatcher is None:
                    # ToDo support status listener
                    self.dispatcher = Dispatcher(self)
                return self.dispatcher
    
    def _set_listener(self):
        """ Set event listener to document. """
        model = self.frame.getController().getModel()
        model.com_sun_star_lang_XComponent_addEventListener(
            DocumentEventListener(self))
    
    def _box_setup(self, box):
        """ Set listeners for box. """
        box.addTextListener(TextListener(self))
        box.addKeyListener(KeyListener(self))
        # ToDo set style change listener
        styles = box.StyleSettings
        self.NORMAL_BG_COLOR = styles.FieldColor
        self.NORMAL_TEXT_COLOR = styles.FieldTextColor
        self.set_color()
    
    def init_state(self, command):
        """ Initialize for command. """
        if command == "Direction":
            self.update_status()
    
    def _update_status(self, status):
        """ Update stateus of direction button. """
        ev = FeatureStateEvent()
        ev.IsEnabled = True
        ev.Requery = False
        ev.Source = self.dispatcher
        ev.State = " ".join(status)
        self.change_event("Direction", ev)
    
    def update_status(self):
        """ Update status by current state. """
        st = []
        if self.backward:
            st.append("<")
        if self.case_sensitive:
            st.append("A")
        if self.migemo_enabled:
            st.append("Mi")
        else:
            if self.regex_enabled:
                st.append("Re")
        self._update_status(st)
    
    def dispose(self):
        self.box = None
        self.descriptor = None
        self.frame = None
        incsearch.frames.remove(self)
        if incsearch.frame.count() == 0:
            self.destroy()
    
    def focus_to_box(self):
        """ Set focus to input box. """
        if self.box:
            self.set_text_from_selection()
            self.box.setFocus()
            self.box.setSelection(Selection(0, 1000))
    
    def focus_to_doc(self):
        """ Set focus back to the document. """
        self.frame.getContainerWindow().setFocus()
    
    def set_text(self, s):
        """ Set text to text field. """
        self.box.setText(s)
    
    def set_color(self, found=True):
        """ Set coloring to text field. """
        if found:
            bg_color = self.NORMAL_BG_COLOR
            text_color = self.NORMAL_TEXT_COLOR
        else:
            bg_color = self.NOT_FOUND_BG_COLOR
            text_color = self.NOT_FOUND_TEXT_COLOR
        self.box.setBackground(bg_color)
        self.box.setForeground(text_color)
    
    def enable_migemo(self, force=False):
        """ Enable migemo to use. """
        if self.migemo_found:
            self.migemo_enabled = force or (not self.migemo_enabled)
            self.update_status()
    
    def enable_backward(self, force=False):
        """ Change search direction to backward. """
        self.backward = force or (not self.backward)
        self.update_status()
    
    def enable_case_sensitive(self, force=False):
        """ Change case sensitivity for searching. """
        self.case_sensitive = force or (not self.case_sensitive)
        self.update_status()
        self.descriptor.SearchCaseSensitive = self.case_sensitive
    
    def enable_regex(self, force=False):
        """ Enable regexp search. """
        self.regex_enabled = force or (not self.regex_enabled)
        self.update_status()
    
    def get_help_text(self, locale):
        """ Get help text for passed locale. """
        if locale.Language == "ja":
            return self.HELP_TEXT_JA
        else:
            return self.HELP_TEXT
    
    def show_help(self):
        """ Show help message in message box. """
        import incsearch.tools
        locale = incsearch.tools.get_current_locale(self.ctx)
        if locale.Language == "ja":
            title = self.HELP_TITLE_JA
        else:
            title = self.HELP_TITLE
        incsearch.tools.show_message(self.ctx, self.frame, 
            self.get_help_text(locale), title)
        if self.__class__.migemo is None:
            self._init()
    
    def start_search(self, search_next=False, opposit=False):
        """ Search with current text. """
        s = self.box.getText()
        if s:
            try:
                self.search(s, search_next=search_next, opposit=opposit)
            except Exception, e:
                print(e)
        else:
            self.set_color()
    
    def migemo_query(self, s):
        """ Query result from migemo. """
        migemo = self.__class__.migemo
        if migemo:
            try:
                return migemo.query(s)
            except Exception, e:
                print("Error on Migemo query: ")
                print(e)
        return s


class WriterSearch(SearchImple):
    """ Searching on Writer document. """
    def _init_descriptor(self):
        self.descriptor = self.frame.getController().getModel().createSearchDescriptor()
    
    def set_text_from_selection(self):
        """ Get text from current selection. """
        controller = self.frame.getController()
        selection = controller.getSelection()
        if selection:
            try:
                if selection.supportsService("com.sun.star.text.TextRanges"):
                    selection = selection.getByIndex(0)
                    s = selection.getString()
                    self.set_text(s[0:100])
            except:
                pass
    
    def search(self, s, search_next=False, opposit=False):
        """ Start searching. """
        controller = self.frame.getController()
        model = controller.getModel()
        descriptor = self.descriptor
        
        backward = self.backward ^ opposit
        descriptor.SearchBackwards = backward
        
        if self.migemo_enabled:
            try:
                s = self.migemo_query(s)
                descriptor.SearchRegularExpression = True
            except:
                pass
        else:
            descriptor.SearchRegularExpression = self.regex_enabled
        descriptor.setSearchString(s)
        
        view_cursor = controller.getViewCursor()
        cursor = view_cursor.getText().createTextCursorByRange(view_cursor)
        if search_next:
            if backward:
                cursor.collapseToStart()
            else:
                cursor.collapseToEnd()
        else:
            if backward:
                cursor.collapseToEnd()
            else:
                cursor.collapseToStart()
        
        found = controller.getModel().findNext(cursor, descriptor)
        if not found and not search_next:
            if backward:
                cursor.gotoEnd(False)
                found = controller.getModel().findNext(cursor, descriptor)
            else:
                found = controller.getModel().findFirst(descriptor)
        if found:
            self.set_color()
            view_cursor.gotoRange(found, False)
        else:
            self.set_color(False)
            view_cursor.collapseToEnd()


class CalcSearch(SearchImple):
    """ Searching on Calc document. """
    CALC_HELP_TEXT = """\
Ctrl + H: Change search direction, "": formula, "V": values, "N": notes
Ctrl + T: Change search type
"""
    CALC_HELP_TEXT_JA = u"""\
Ctrl + H: 検索方向変更、"": 行、"C": 列
Ctrl + T: 検索する値の種類変更、"": 数式、"V": 値、"N": ノート
"""
    
    def __init__(self, ctx, frame):
        self.search_direction = True # in rows
        self.search_type = 0 # formula: 0, values: 1, notes: 2
        SearchImple.__init__(self, ctx, frame)
        self.helper = None
    
    def set_text_from_selection(self):
        """ Set text from current selection. """
        controller = self.frame.getController()
        selection = controller.getSelection()
        if selection:
            try:
                if selection.supportsService("com.sun.star.sheet.SheetCell"):
                    s = selection.getString()
                    self.set_text(s[0:100])
            except:
                pass
    
    def update_status(self):
        st = []
        if self.backward:
            st.append("<")
        if self.case_sensitive:
            st.append("A")
        if not self.search_direction:
            st.append("C")
        if self.search_type > 0:
            st.append(["", "V", "N"][self.search_type])
        if self.migemo_enabled:
            st.append("Mi")
        else:
            if self.regex_enabled:
                st.append("Re")
        self._update_status(st)
    
    def change_search_direction(self):
        self.search_direction = not self.search_direction
        self.update_status()
        self.descriptor.SearchByRow = self.search_direction
    
    def change_search_type(self):
        self.search_type += 1
        if self.search_type > 2:
            self.search_type = 0
        self.update_status()
        self.descriptor.SearchType = self.search_type
    
    def get_help_text(self, locale):
        if locale.Language == "ja":
            return self.HELP_TEXT_JA + self.CALC_HELP_TEXT_JA
        else:
            return self.HELP_TEXT + self.CALC_HELP_TEXT
    
    def _init_descriptor(self):
        self.descriptor = self.frame.getController().\
                getActiveSheet().createSearchDescriptor()
        self.descriptor.SearchByRow = self.search_direction
        self.descriptor.SearchType = self.search_type
    
    def search(self, s, search_next=False, opposit=False):
        controller = self.frame.getController()
        model = controller.getModel()
        descriptor = self.descriptor
        
        backward = self.backward ^ opposit
        descriptor.SearchBackwards = backward
        
        if self.migemo_enabled:
            try:
                s = self.migemo_query(s)
                descriptor.SearchRegularExpression = True
            except:
                pass
        else:
            descriptor.SearchRegularExpression = self.regex_enabled
        descriptor.setSearchString(s)
        
        obj = controller.getSelection()
        try:
            if not obj.supportsService("com.sun.star.sheet.SheetCellRange"):
                return
        except:
            return
        sheet = controller.getActiveSheet()
        
        if obj.supportsService("com.sun.star.sheet.SheetCell"):
            addr = obj.getRangeAddress()
            column = addr.StartColumn
            row = addr.StartRow
        else:
            data = self.get_cursor_position(controller, sheet)
            if data:
                column = data[0]
                row = data[1]
            else:
                # begin with left top corner
                addr = obj.getCellByPosition(0, 0).getRangeAddress()
                column = addr.StartColumn
                row = addr.StartRow
        
        if column == 0 and row == 0:
            found = sheet.findFirst(descriptor)
        else:
            if not search_next:
                if self.search_direction:
                    column -= 1
                else:
                    row -= 1
                if column < 0 or row < 0:
                    cursor = sheet.createCursor()
                    cursor.gotoStartOfUsedArea(False)
                    cursor.gotoEndOfUsedArea(True)
                    if column < 0:
                        row -= 1
                        column = cursor.getRangeAddress().EndColumn
                    elif row < 0:
                        column -= 1
                        row = cursor.getRangeAddress().EndRow
            
            found = sheet.findNext(
                sheet.getCellByPosition(column, row), descriptor)
        if not found and not search_next:
            cursor = sheet.createCursor()
            if backward:
                cursor = sheet.createCursor()
                cursor.gotoEndOfUsedArea(False)
                found = sheet.findNext(cursor, descriptor)
            else:
                found = sheet.findFirst(descriptor)
        if found:
            if self.helper is None:
                self.helper = self.ctx.getServiceManager().createInstanceWithContext(
                    "com.sun.star.frame.DispatchHelper", self.ctx)
            self.helper.executeDispatch(
                self.frame, ".uno:GoToCell", "_self", 0, 
                (PropertyValue("ToPoint", -1, found.AbsoluteName, 0),))
            self.set_color()
        else:
            self.set_color(False)
    
    def get_cursor_position(self, controller, cell_range):
        """ Get current cursor position. """
        index = cell_range.getRangeAddress().Sheet
        try:
            parts = controller.getViewData().split(";", 4 + index)
            data = parts[3 + index].split("/", 3)
            return (int(data[0]), int(data[1])) # column, row
        except:
            return None

