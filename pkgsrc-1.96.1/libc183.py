def ed(p,a,b):
    s=open(p).read(); assert s.count(a)==1,(p,a); s=s.replace(a,b); open(p,"w").write(s)
p="src/unix/mod.rs"
ed(p,'    } else if #[cfg(target_os = "nto")] {\n        pub type uid_t = i32;','    } else if #[cfg(any(target_os = "nto", target_os = "irix"))] {\n        pub type uid_t = i32;')
ed(p,'    #[cfg_attr(musl32_time64, link_name = "__dlsym_time64")]\n    pub fn dlsym(','    #[cfg_attr(musl32_time64, link_name = "__dlsym_time64")]\n    #[cfg_attr(target_os = "irix", link_name = "__irix_dlsym")]\n    pub fn dlsym(')
# 0.2.183's f!/safe_f! take plain `pub fn`/`pub const fn` (0.2.189 spells out unsafe/safe);
# only inside those macro calls (siginfo_t's accessors stay unsafe)
import re
p = "src/unix/irix/mod.rs"
s = open(p).read()
def plain(m):
    b = m.group(0)
    for x, y in [("pub const unsafe fn ", "pub const fn "), ("pub unsafe fn ", "pub fn "),
                 ("pub const safe fn ", "pub const fn "), ("pub safe fn ", "pub fn ")]:
        b = b.replace(x, y)
    return b
s = re.sub(r"(?ms)^(safe_)?f! \{\n.*?^\}\n", plain, s)
open(p, "w").write(s)
