use tokio::io::{AsyncReadExt, AsyncWriteExt};
#[tokio::main]
async fn main() {
    let l = tokio::net::TcpListener::bind("127.0.0.1:0").await.unwrap();
    let a = l.local_addr().unwrap();
    let srv = tokio::spawn(async move {
        let (mut s, _) = l.accept().await.unwrap();
        let mut b = [0u8; 5]; s.read_exact(&mut b).await.unwrap();
        s.write_all(&b.to_ascii_uppercase()).await.unwrap();
    });
    let mut c = tokio::net::TcpStream::connect(a).await.unwrap();
    c.write_all(b"tokio").await.unwrap();
    let mut b = [0u8; 5]; c.read_exact(&mut b).await.unwrap();
    srv.await.unwrap();
    let t0 = std::time::Instant::now();
    tokio::time::sleep(std::time::Duration::from_millis(100)).await;
    let out = tokio::process::Command::new("/sbin/uname").arg("-sr").output().await.unwrap();
    println!("tokio on {}: echo {:?}, sleep {:?}, uname {:?}", a, std::str::from_utf8(&b).unwrap(), t0.elapsed(), String::from_utf8_lossy(&out.stdout).trim());
}
