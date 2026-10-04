use std::time::Duration;
macro_rules! t { ($r:ident, $n:expr, $to:expr) => {{
    use $r::fs::{self, Mode, OFlags, CWD};
    let pid = $r::process::getpid();
    let uid = $r::process::getuid();
    let st = fs::stat("/usr/include/stdio.h").unwrap();
    let dirfd = fs::openat(CWD, "/usr/include", OFlags::RDONLY | OFlags::DIRECTORY, Mode::empty()).unwrap();
    let st2 = fs::statat(&dirfd, "stdio.h", fs::AtFlags::empty()).unwrap();
    let mut n = 0;
    for e in fs::Dir::read_from(&dirfd).unwrap() { let _ = e.unwrap(); n += 1; }
    let now = $r::time::clock_gettime($r::time::ClockId::Monotonic);
    let (r, w) = $r::pipe::pipe().unwrap();
    $r::io::write(&w, b"pipe!").unwrap();
    let mut buf = [0u8; 5];
    let mut pfd = [$r::event::PollFd::new(&r, $r::event::PollFlags::IN)];
    let ready = $r::event::poll(&mut pfd, $to).unwrap();
    $r::io::read(&r, &mut buf).unwrap();
    let sock = $r::net::socket($r::net::AddressFamily::INET, $r::net::SocketType::STREAM, None).unwrap();
    let local = $r::net::getsockname(&sock).unwrap();
    let m = unsafe { $r::mm::mmap_anonymous(std::ptr::null_mut(), 16384, $r::mm::ProtFlags::READ | $r::mm::ProtFlags::WRITE, $r::mm::MapFlags::PRIVATE).unwrap() };
    unsafe { *(m as *mut u32) = 0xdeadbeef; $r::mm::munmap(m, 16384).unwrap(); }
    println!("{}: pid {:?} uid {:?}, stdio.h {} bytes = {} at, {} entries, monotonic {}s, poll {} read {:?}, socket {:?}, mmap ok",
        $n, pid, uid.as_raw(), st.st_size, st2.st_size, n, now.tv_sec, ready, std::str::from_utf8(&buf).unwrap(), local);
}}; }
fn main() { t!(r1, "rustix 1", None); t!(r038, "rustix 0.38", -1); let _ = Duration::from_secs(1); }
