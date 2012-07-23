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

from com.sun.star.lang import Locale, XServiceInfo, XInitialization


class ServiceInfo(XServiceInfo):
    
    # XServiceInfo
    def getImplementationName(self):
        return self.IMPLE_NAME
    
    def getSupportedServiceNames(self):
        return self.SERVICE_NAMES
    
    def supportsService(self, name):
        return name in self.SERVICE_NAMES

class ServiceBase(XServiceInfo, XInitialization):
    pass


def create_service(ctx, name, args=None):
    smgr = ctx.getServiceManager()
    if args:
        return smgr.createInstanceWithArgumentsAndContext(name, args, ctx)
    else:
        return smgr.createInstanceWithContext(name, ctx)


from com.sun.star.awt import Rectangle
def show_message(ctx, frame, message, title="", type="messbox", buttons=1):
    """ Show text in message box. """
    #from com.sun.star.awt import Rectangle
    try:
        peer = frame.getContainerWindow()
    except:
        peer = frame
    box = peer.getToolkit().createMessageBox(
        peer, Rectangle(), type, buttons, title, message)
    n = box.execute()
    box.dispose()
    return n


from com.sun.star.beans import PropertyValue
def get_config(ctx, nodepath, modifiable=False):
    cp = create_service(ctx, "com.sun.star.configuration.ConfigurationProvider")
    node = PropertyValue("nodepath", -1, nodepath, 0)
    if modifiable:
        name = "com.sun.star.configuration.ConfigurationUpdateAccess"
    else:
        name = "com.sun.star.configuration.ConfigurationAccess"
    config = cp.createInstanceWithArguments(name, (node,))
    return config


def get_config_value(ctx, nodepath, name):
    """ Get value from specific configuration node. """
    config = get_config(ctx, nodepath)
    return config.getPropertyValue(name)


def get_current_locale(ctx):
    """ Get current locale. """
    config = get_config(ctx, "/org.openoffice.Setup/L10N")
    locale = config.getPropertyValue("ooLocale")
    parts = locale.split("-")
    lang = parts[0]
    country = ""
    if len(parts) == 2:
        country = parts[1]
    return Locale(lang, country, "")

