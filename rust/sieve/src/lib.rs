//#![feature(test)]
//extern crate test;

//pub struct Sieve;
//impl Sieve {
//	pub fn primes_up_to(max: usize) -> Vec<usize> {
//		if max < 2 {
//			return vec![]
//		}
//
//		// Optimization could be done by leaving out even values,
//		// but step_by is an unstable feature and so is the inclusive
//        // range (...)
//		let mut result: Vec<usize> = (2..max+1).collect();
//
//		for number in 2..max+1 {
//			result.retain(|&x| x == number || x%number > 0);
//		}
//
//		result.clone()
//	}
//}
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



//#[cfg(test)]
//mod tests {
//    use super::*;
//    use test::Bencher;
//
//    #[test]
//    fn it_works() {
//    }
//
//    #[bench]
//    fn bench_sieve(b: &mut Bencher) {
//        b.iter(|| Sieve::primes_up_to(10000));
//    }
//}
