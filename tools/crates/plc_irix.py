# IRIX in parking_lot_core: no pthread_condattr_setclock, so (as on Android)
# condvar timeouts are CLOCK_REALTIME times.
import sys
p = sys.argv[1] + "/src/thread_parker/unix.rs"
s = open(p).read()
for a, b in [
    ('#[cfg(any(target_vendor = "apple", target_os = "android", target_os = "espidf"))]',
     '#[cfg(any(target_vendor = "apple", target_os = "android", target_os = "espidf", target_os = "irix"))]'),
    ('#[cfg(not(any(target_vendor = "apple", target_os = "android", target_os = "espidf")))]',
     '#[cfg(not(any(target_vendor = "apple", target_os = "android", target_os = "espidf", target_os = "irix")))]'),
    ('let clock = if cfg!(target_os = "android") {',
     'let clock = if cfg!(any(target_os = "android", target_os = "irix")) {'),
]:
    assert s.count(a) == 1, a
    s = s.replace(a, b)
open(p, "w").write(s)
print("ok")
