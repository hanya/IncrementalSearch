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

def create(ctx, *args):
    try:
        import incsearch.toolbar
        return incsearch.toolbar.IncrementalSearchToolbarController(
            ctx, args)
    except Exception, e:
        print(e)

def create_ph(ctx, *args):
    try:
        import incsearch.ph
        return incsearch.ph.IncrementalSearchProtocolHandler(ctx, args)
    except Exception, e:
        print(e)

def create_option_handler(ctx, *args):
    try:
        import incsearch.options
        return incsearch.options.OptionsPageHandler(ctx, args)
    except Exception, e:
        print(e)

import incsearch

g_ImplementationHelper = unohelper.ImplementationHelper()

g_ImplementationHelper.addImplementation(
    create, incsearch.IMPLE_NAME, incsearch.SERVICE_NAMES)

g_ImplementationHelper.addImplementation(
    create_ph, incsearch.PH_IMPLE_NAME, incsearch.PH_SERVICE_NAMES)

g_ImplementationHelper.addImplementation(
    create_option_handler, incsearch.OPTION_IMPLE_NAME, (incsearch.OPTION_IMPLE_NAME,))

