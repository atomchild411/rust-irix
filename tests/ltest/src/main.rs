fn main() {
    unsafe {
        let l = l07::Library::new("libm.so").unwrap();
        let cos: l07::Symbol<extern "C" fn(f64) -> f64> = l.get(b"cos").unwrap();
        println!("libloading 0.7: cos(0) = {}", cos(0.0));
        let l = l08::Library::new("libm.so").unwrap();
        let cos: l08::Symbol<extern "C" fn(f64) -> f64> = l.get(b"cos").unwrap();
        println!("libloading 0.8: cos(1) = {}", cos(1.0));
    }
}
