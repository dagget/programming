use std::convert::TryInto;

pub fn is_armstrong_number(num: u32) -> bool {
    let mut n = num;
    let mut v = vec![];

    while n > 0 {
        v.push(n % 10);
        n /= 10;
    }

    v.iter()
     .map(|&x| x.pow(v.len().try_into().unwrap()))
     .sum::<u32>() == num
}
