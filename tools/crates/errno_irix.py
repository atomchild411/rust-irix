# IRIX in the errno crate: the calling thread's errno is at __oserror().
import sys
p = sys.argv[1] + "/src/unix.rs"
s = open(p).read()
a = '    #[cfg_attr(target_os = "aix", link_name = "_Errno")]\n'
assert s.count(a) == 1
s = s.replace(a, a + '    #[cfg_attr(target_os = "irix", link_name = "__oserror")]\n')
open(p, "w").write(s)
print("ok")
