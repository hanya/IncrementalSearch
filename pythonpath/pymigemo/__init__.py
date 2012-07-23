
import sys
import platform

Migemo = None

sys_platform = sys.platform
if sys_platform.startswith("linux"):
    pf = "linux"
    if platform.architecture()[0] == "64bit":
        arc = "x86_64"
    else:
        arc = "x86"
elif sys_platform.startswith("win"):
    pf = "windows"
    arc = "x86"
if sys.maxunicode > 0xffff:
    u = "ucs4"
else:
    u = "ucs2"
version = str(sys.version_info[0]) + str(sys.version_info[1])
name = "_".join((pf, arc, u, version))
try:
    mod = __import__("pymigemo." + name + ".migemo")
    mod = getattr(mod, name)
    mod = getattr(mod, "migemo")
    Migemo = mod.Migemo
except:
    pass

del name
del pf
del version
del arc
del platform
del sys_platform
del sys
