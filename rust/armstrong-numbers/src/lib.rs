pub fn is_armstrong_number(num: u32) -> bool {
    let mut n = num;
    let mut v = vec![];

    while n > 0 {
        v.push(n % 10);
        n /= 10;
    }

    v.iter()
     .fold(0, |s,x| s + x.pow(v.len() as u32)) == num
}
