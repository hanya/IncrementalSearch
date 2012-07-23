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

IMPLE_NAME = "mytools.search.IncrementalSearch"
SERVICE_NAMES = ("com.sun.star.frame.ToolbarController", )

PH_IMPLE_NAME = "mytools.search.IncrementalSearchProtocolHandler"
PH_SERVICE_NAMES = ("com.sun.star.frame.ProtocolHandler", )

PROTOCOL = "mytools.search:"
INC_PATH = "IncrementalSearch"

OPTION_IMPLE_NAME = "incsearch.OptionsPageHandler"

CONFIG_NODE_SETTINGS = "/mytools.IncrementalSearch/Settings"
NAME_DICTIONARY = "Dictionary"

PH_PROTOCOL = "mytools.search.IncrementalSearch:"

import incsearch.frames
frames = incsearch.frames.FrameKeeper("incsearch.imple.create_imple")
