macro_rules! t { ($m:ident, $n:expr) => {{
    use $m::{Domain, Socket, Type};
    let s = Socket::new(Domain::IPV4, Type::STREAM, None).unwrap();
    s.set_reuse_address(true).unwrap();
    s.bind(&"127.0.0.1:0".parse::<std::net::SocketAddr>().unwrap().into()).unwrap();
    s.listen(4).unwrap();
    let a = s.local_addr().unwrap().as_socket().unwrap();
    s.set_nonblocking(true).unwrap();
    println!("{}: listening on {}, keepalive {:?}", $n, a, s.keepalive());
}}; }
fn main() { t!(s04, "socket2 0.4"); t!(s05, "socket2 0.5"); t!(s06, "socket2 0.6"); }
