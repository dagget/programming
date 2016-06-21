pub struct Sieve;
impl Sieve {
	pub fn primes_up_to(max: usize) -> Vec<usize> {
		if max < 2 {
			return vec![]
		}

		// Optimization could be done by leaving out even values,
		// but step_by is an unstable feature and so is the inclusive
        // range (...)
		let mut result: Vec<usize> = (2..max+1).collect();

		for number in 2..max+1 {
			result.retain(|&x| x == number || x%number > 0);
		}

		result.clone()
	}
}
