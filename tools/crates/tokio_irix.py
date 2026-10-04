# IRIX in tokio: no peer credentials for UNIX-domain sockets (an error, not the uid 0 that the
# no-process platforms answer).
import sys
p = sys.argv[1] + '/src/net/unix/ucred.rs'
s = open(p).read()
a = '#[cfg(target_os = "nto")]\npub(crate) use self::impl_nto::get_peer_cred;\n'
assert s.count(a) == 1
s = s.replace(a, a + '\n#[cfg(target_os = "irix")]\npub(crate) use self::impl_irix::get_peer_cred;\n')
s = s.rstrip('\n') + '''

// IRIX cannot tell who is at the other end of a UNIX-domain socket.
#[cfg(target_os = "irix")]
pub(crate) mod impl_irix {
    use crate::net::unix::UnixStream;
    use std::io;

    pub(crate) fn get_peer_cred(_sock: &UnixStream) -> io::Result<super::UCred> {
        Err(io::Error::new(
            io::ErrorKind::Unsupported,
            "IRIX has no peer credentials for UNIX-domain sockets",
        ))
    }
}
'''
open(p, 'w').write(s)
# uid_t and gid_t are signed on IRIX, as on QNX
p = sys.argv[1] + '/src/process/mod.rs'
s = open(p).read()
a = '#[cfg(target_os = "nto")]\n        let id = id as i32;'
assert s.count(a) == 2
s = s.replace(a, '#[cfg(any(target_os = "nto", target_os = "irix"))]\n        let id = id as i32;')
open(p, 'w').write(s)
print('ok')
