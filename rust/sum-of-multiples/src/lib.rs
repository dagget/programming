use std::collections::HashMap;

pub fn sum_of_multiples(max: u64, numbers: &[u64]) -> u64 {
    let mut h = HashMap::new();

    for x in numbers.iter() { 
        let mut y = *x;

        if y > 0 {
            while y < max {
               h.insert(y,1);
               y += *x;
            }
        }
    };

    h.keys().sum()
}
