use std::convert::TryInto;

pub struct Sieve;

impl Sieve{
    pub fn primes_up_to(max:usize) -> Vec<usize>{
        let n = max+1;
        let mut sieve = vec![true;n];
        let sqn = f64::sqrt(n as f64) as usize;
        (2..n).filter(|&i|{
            if i <= sqn && sieve[i] {
                let mut j = i+i;
                while j < n {
                    sieve[j]=false;
                    j+=i;
                }                    
            };
            sieve[i]
        })
        .collect()
    }   
}

pub fn nth(n: u32) -> u32 {
    let n: usize = n.try_into().unwrap();

    if n == 0 {
        return 2;
    }

    let mut max = 10;
    let mut v = Sieve::primes_up_to(max);

    while v.len() < n {
        v = Sieve::primes_up_to(max);
        max *= 10;
    }

    v[n].try_into().unwrap()
    
}
