use std::time::Duration;
macro_rules! miotest { ($m:ident, $name:expr) => {{
    use $m::{Events, Interest, Poll, Token};
    let mut poll = Poll::new().unwrap();
    let mut l = $m::net::TcpListener::bind("127.0.0.1:0".parse().unwrap()).unwrap();
    poll.registry().register(&mut l, Token(0), Interest::READABLE).unwrap();
    let addr = l.local_addr().unwrap();
    let _c = std::net::TcpStream::connect(addr).unwrap();
    let mut ev = Events::with_capacity(8);
    poll.poll(&mut ev, Some(Duration::from_secs(5))).unwrap();
    let got = ev.iter().any(|e| e.token() == Token(0) && e.is_readable());
    let acc = l.accept().map(|(_, a)| a.to_string());
    println!("{}: readable event {}, accept {:?}", $name, got, acc);
}}; }
fn main() {
    let mut a = [0u8; 4]; gr02::getrandom(&mut a).unwrap();
    let mut b = [0u8; 4]; gr03::fill(&mut b).unwrap();
    let mut c = [0u8; 4]; gr04::fill(&mut c).unwrap();
    println!("getrandom {:02x?} {:02x?} {:02x?}", a, b, c);
    miotest!(mio08, "mio 0.8");
    miotest!(mio1, "mio 1");
}
