#![feature(test)]
extern crate test;

pub fn factors(n: u64) -> Vec<u64> {
    let mut factors: Vec<u64> = vec![];
    let mut remainder: u64 = n;

    // 0 and 1 are not considered prime
    if n < 2 {
        return factors;
    }

    // only calculate up to n/2 as factor
    // multiplication mirrors
    for divisor in 2 ..= n/2 {
        // start with lowest prime first
        // to ensure non-primes are factored
        // out automatically.
        while remainder % divisor == 0 {
            remainder /= divisor;
            factors.push(divisor);
        }
        if remainder <= 1 {
            break;
        }
    }

    // if remainder (or n) is a prime 
    if remainder > 1 {
        factors.push(remainder);
    }

    factors
}

#[cfg(test)]
mod tests {
    use super::*;
    use test::Bencher;

    #[bench]
    fn bench_factors(b: &mut Bencher) {
        b.iter(|| factors(93_819_012_551));
    }
}
