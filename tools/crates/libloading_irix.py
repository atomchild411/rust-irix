# IRIX's <dlfcn.h> values in libloading: RTLD_LAZY 1, RTLD_NOW 2, RTLD_GLOBAL 4, RTLD_LOCAL 0.
import re, sys
p = sys.argv[1] + "/src/os/unix/consts.rs"
s = open(p).read()
for name, val in [("RTLD_LAZY", 1), ("RTLD_NOW", 2), ("RTLD_GLOBAL", 4), ("RTLD_LOCAL", 0)]:
    # the cfg_if! that defines it per system (not the documentation stand-ins, = !0)
    m = re.search(r"cfg_if! \{\n(\s*)if #\[cfg\((?:(?!cfg_if!).)*?pub\(super\) const %s: c_int = (?!!0)" % name, s, re.S)
    assert m, name
    ind = m.group(1)
    at = m.start() + len("cfg_if! {\n")
    s = (s[:at] + ind + 'if #[cfg(target_os = "irix")] {\n' + ind + '    pub(super) const %s: c_int = %d;\n' % (name, val)
         + ind + '} else ' + s[at + len(ind):])
open(p, "w").write(s)
print("ok")
