def ed(p,a,b):
    s=open(p).read(); assert s.count(a)==1,(p,a); s=s.replace(a,b); open(p,"w").write(s)
S="compiler/rustc_target/src/spec/"
ed(S+"base/mod.rs","pub(crate) mod illumos;\n","pub(crate) mod illumos;\npub(crate) mod irix;\n")
ed(S+"mod.rs",'    ("powerpc64-ibm-aix", powerpc64_ibm_aix),\n','    ("mips64-sgi-irix", mips64_sgi_irix),\n    ("powerpc64-ibm-aix", powerpc64_ibm_aix),\n')
ed(S+"mod.rs",'        Illumos = "illumos",\n','        Illumos = "illumos",\n        Irix = "irix",\n')
ed(S+"mod.rs",'        Abi64 = "abi64",\n','        Abi64 = "abi64",\n        AbiN32 = "abin32",\n')
ed(S+"mod.rs","| (LlvmAbi::N32, CfgAbi::Unspecified | CfgAbi::Other(_)),","| (LlvmAbi::N32, CfgAbi::Unspecified | CfgAbi::AbiN32 | CfgAbi::Other(_)),")
ed("src/bootstrap/src/core/sanity.rs",'    "x86_64-unknown-linux-gnumsan",\n','    "mips64-sgi-irix",\n    "x86_64-unknown-linux-gnumsan",\n')
ed("src/librustdoc/clean/cfg.rs",'        Illumos => "illumos",\n','        Illumos => "illumos",\n        Irix => "IRIX",\n')
