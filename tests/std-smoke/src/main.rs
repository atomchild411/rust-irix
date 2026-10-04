// std on IRIX: one line per check, PASS or FAIL with the reason.
use std::collections::HashMap;
use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream, ToSocketAddrs, UdpSocket};
use std::process::{Command, Stdio};
use std::sync::{mpsc, Arc, Condvar, Mutex};
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};
use std::{env, fs, thread};

type R = Result<String, String>;

fn e<E: std::fmt::Display>(x: E) -> String {
    x.to_string()
}

fn check(name: &str, f: fn() -> R, fails: &mut u32) {
    match f() {
        Ok(s) => println!("PASS {name}: {s}"),
        Err(s) => {
            *fails += 1;
            println!("FAIL {name}: {s}")
        }
    }
}

fn args_env() -> R {
    let a: Vec<String> = env::args().collect();
    let path = env::var("PATH").map_err(|x| format!("args_env#1: {x}"))?;
    let n = env::vars().count();
    unsafe { env::set_var("SMOKE", "1") };
    if env::var("SMOKE").as_deref() != Ok("1") {
        return Err("set_var".into());
    }
    Ok(format!("argv {a:?}, {n} vars, PATH {} bytes, cwd {:?}, exe {:?}", path.len(),
        env::current_dir().map_err(|x| format!("args_env#2: {x}"))?, env::current_exe().map_err(|x| format!("args_env#3: {x}"))?))
}

fn files() -> R {
    let d = env::temp_dir().join(format!("smoke-{}", std::process::id()));
    fs::create_dir_all(d.join("sub")).map_err(|x| format!("files#1: {x}"))?;
    let f = d.join("a.txt");
    fs::write(&f, b"hello irix\n").map_err(|x| format!("files#2: {x}"))?;
    let mut s = String::new();
    fs::File::open(&f).map_err(|x| format!("files#3: {x}"))?.read_to_string(&mut s).map_err(|x| format!("files#4: {x}"))?;
    if s != "hello irix\n" {
        return Err(format!("read back {s:?}"));
    }
    let m = fs::metadata(&f).map_err(|x| format!("files#5: {x}"))?;
    let age = SystemTime::now().duration_since(m.modified().map_err(|x| format!("files#6: {x}"))?).map_err(|x| format!("files#7: {x}"))?;
    fs::rename(&f, d.join("b.txt")).map_err(|x| format!("files#8: {x}"))?;
    std::os::unix::fs::symlink("b.txt", d.join("link")).map_err(|x| format!("files#9: {x}"))?;
    let target = fs::read_link(d.join("link")).map_err(|x| format!("files#10: {x}"))?;
    let canon = fs::canonicalize(d.join("link")).map_err(|x| format!("files#11: {x}"))?;
    let mut names: Vec<String> = fs::read_dir(&d).map_err(|x| format!("files#12: {x}"))?
        .map(|x| x.map(|x| x.file_name().to_string_lossy().into_owned()))
        .collect::<Result<_, _>>().map_err(|x| format!("files#13: {x}"))?;
    names.sort();
    let isdir = fs::read_dir(&d).map_err(|x| format!("files#14: {x}"))?.filter_map(|x| x.ok())
        .filter(|x| x.file_type().map(|t| t.is_dir()).unwrap_or(false)).count();
    use std::os::unix::fs::PermissionsExt;
    fs::set_permissions(d.join("b.txt"), fs::Permissions::from_mode(0o600)).map_err(|x| format!("files#15: {x}"))?;
    let mode = fs::metadata(d.join("b.txt")).map_err(|x| format!("files#16: {x}"))?.permissions().mode() & 0o777;
    let mut af = fs::OpenOptions::new().append(true).open(d.join("b.txt")).map_err(|x| format!("files#17: {x}"))?;
    af.write_all(b"more\n").map_err(|x| format!("files#18: {x}"))?;
    let len = fs::metadata(d.join("b.txt")).map_err(|x| format!("files#19: {x}"))?.len();
    fs::remove_dir_all(&d).map_err(|x| format!("files#20: {x}"))?;
    if d.exists() {
        return Err("remove_dir_all left it".into());
    }
    Ok(format!("len {} -> {len}, age {age:?}, link -> {target:?} = {canon:?}, entries {names:?} ({isdir} dir), mode {mode:o}", m.len()))
}

fn threads() -> R {
    let n = thread::available_parallelism().map_err(e)?;
    let total = Arc::new(Mutex::new(0u64));
    let hs: Vec<_> = (0..8u64).map(|i| {
        let t = total.clone();
        thread::Builder::new().name(format!("w{i}")).spawn(move || {
            for k in 0..10_000u64 {
                *t.lock().unwrap() += k % 7 + i;
            }
            thread::current().name().map(String::from)
        }).unwrap()
    }).collect();
    let names: Vec<_> = hs.into_iter().map(|h| h.join().unwrap()).collect();
    let got = *total.lock().unwrap();
    let want: u64 = (0..8u64).map(|i| (0..10_000u64).map(|k| k % 7 + i).sum::<u64>()).sum();
    if got != want {
        return Err(format!("sum {got} != {want}"));
    }
    let (tx, rx) = mpsc::channel();
    for i in 0..4 {
        let tx = tx.clone();
        thread::spawn(move || tx.send(i * i).unwrap());
    }
    drop(tx);
    let mut v: Vec<i32> = rx.iter().collect();
    v.sort();
    Ok(format!("parallelism {n}, sum {got}, names {:?}, channel {v:?}", &names[..2]))
}

fn condvar_sleep() -> R {
    let pair = Arc::new((Mutex::new(false), Condvar::new()));
    let p2 = pair.clone();
    let t0 = Instant::now();
    let (g, res) = pair.1.wait_timeout(pair.0.lock().unwrap(), Duration::from_millis(200)).unwrap();
    drop(g);
    let waited = t0.elapsed();
    if !res.timed_out() || waited < Duration::from_millis(190) {
        return Err(format!("wait_timeout {waited:?} timed_out {}", res.timed_out()));
    }
    let h = thread::spawn(move || {
        thread::sleep(Duration::from_millis(50));
        *p2.0.lock().unwrap() = true;
        p2.1.notify_one();
    });
    let mut g = pair.0.lock().unwrap();
    while !*g {
        g = pair.1.wait(g).unwrap();
    }
    drop(g);
    h.join().unwrap();
    let t1 = Instant::now();
    thread::sleep(Duration::from_millis(100));
    let slept = t1.elapsed();
    let now = SystemTime::now().duration_since(UNIX_EPOCH).map_err(e)?;
    Ok(format!("timeout after {waited:?}, notified, sleep(100ms) took {slept:?}, epoch {}s", now.as_secs()))
}

fn process() -> R {
    let out = Command::new("/sbin/echo").args(["one", "two"]).output()
        .or_else(|_| Command::new("echo").args(["one", "two"]).output()).map_err(e)?;
    let st = Command::new("false").status().map_err(e)?;
    let mut cat = Command::new("cat").stdin(Stdio::piped()).stdout(Stdio::piped()).spawn().map_err(e)?;
    cat.stdin.take().unwrap().write_all(b"through cat").map_err(e)?;
    let co = cat.wait_with_output().map_err(e)?;
    let sh = Command::new("/bin/sh").args(["-c", "echo $SMOKE_X; exit 3"]).env("SMOKE_X", "envok")
        .output().map_err(e)?;
    Ok(format!("echo {:?} {}, false {st}, cat {:?}, sh {:?} {}",
        String::from_utf8_lossy(&out.stdout), out.status, String::from_utf8_lossy(&co.stdout),
        String::from_utf8_lossy(&sh.stdout), sh.status))
}

fn net() -> R {
    let l = TcpListener::bind("127.0.0.1:0").map_err(|x| format!("net#1: {x}"))?;
    let addr = l.local_addr().map_err(|x| format!("net#2: {x}"))?;
    let h = thread::spawn(move || {
        let (mut s, peer) = l.accept().unwrap();
        let mut b = [0u8; 5];
        s.read_exact(&mut b).unwrap();
        s.write_all(&b.map(|c| c.to_ascii_uppercase())).unwrap();
        peer
    });
    let mut c = TcpStream::connect(addr).map_err(|x| format!("net#3: {x}"))?;
    // IRIX has no SO_RCVTIMEO/SO_SNDTIMEO (ENOPROTOOPT, from C too).
    let rto = c.set_read_timeout(Some(Duration::from_secs(5))).err().map(|x| x.to_string());
    c.write_all(b"hello").map_err(|x| format!("net#5: {x}"))?;
    let mut b = [0u8; 5];
    c.read_exact(&mut b).map_err(|x| format!("net#6: {x}"))?;
    let peer = h.join().unwrap();
    let u1 = UdpSocket::bind("127.0.0.1:0").map_err(|x| format!("net#7: {x}"))?;
    let u2 = UdpSocket::bind("127.0.0.1:0").map_err(|x| format!("net#8: {x}"))?;
    u1.send_to(b"dgram", u2.local_addr().map_err(|x| format!("net#9: {x}"))?).map_err(|x| format!("net#10: {x}"))?;
    let mut ub = [0u8; 16];
    let (n, from) = u2.recv_from(&mut ub).map_err(|x| format!("net#12: {x}"))?;
    let lh: Vec<_> = "localhost:80".to_socket_addrs().map_err(|x| format!("net#13: {x}"))?.collect();
    Ok(format!("tcp {addr} <- {peer}: {:?}; udp {:?} from {from}; localhost {lh:?}; read timeout error {rto:?}",
        String::from_utf8_lossy(&b), String::from_utf8_lossy(&ub[..n])))
}

fn misc() -> R {
    let mut m = HashMap::new();
    for i in 0..1000 {
        m.insert(format!("k{i}"), i);
    }
    let s: i32 = m.values().sum();
    let f = (2.0f64).sqrt() * 1e10;
    let v: Vec<u64> = (1..=20).map(|x: u64| x.pow(3)).collect();
    Ok(format!("hashmap sum {s}, sqrt2e10 {f:.3}, {:e}, i128 {}, cubes end {:?}", 1.5e-7f32,
        u128::MAX / 3, &v[17..]))
}

fn unwinding() -> R {
    std::panic::set_hook(Box::new(|_| {}));
    let caught = std::panic::catch_unwind(|| {
        let v: Vec<i32> = Vec::new();
        v[std::hint::black_box(5)]
    });
    let msg = match &caught {
        Err(p) => p.downcast_ref::<String>().cloned().unwrap_or_default(),
        Ok(_) => return Err("no panic".into()),
    };
    let t = thread::spawn(|| -> i32 { panic!("in a thread") }).join();
    let _ = std::panic::take_hook();
    let bt = std::backtrace::Backtrace::force_capture().to_string();
    let frames = bt.lines().filter(|l| l.trim_start().chars().next().map_or(false, |c| c.is_ascii_digit())).count();
    if t.is_ok() || frames == 0 {
        return Err(format!("thread join {:?}, {frames} frames:\n{bt}", t.is_ok()));
    }
    Ok(format!("caught {msg:?}, thread panic joined as Err, backtrace {frames} frames"))
}

fn main() {
    let mut fails = 0;
    check("args+env", args_env, &mut fails);
    check("fs", files, &mut fails);
    check("threads", threads, &mut fails);
    check("condvar+time", condvar_sleep, &mut fails);
    check("process", process, &mut fails);
    check("net", net, &mut fails);
    check("misc", misc, &mut fails);
    check("unwinding", unwinding, &mut fails);
    println!("{fails} failed");
    if env::args().any(|a| a == "panic") {
        let v: Vec<i32> = Vec::new();
        println!("{}", v[std::hint::black_box(3)]);
    }
    std::process::exit(fails as i32);
}
