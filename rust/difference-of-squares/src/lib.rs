pub fn square_of_sum(upper: u64) -> u64 {
    (1..upper+1).fold(0, |acc, x| acc + x).pow(2)
}

pub fn sum_of_squares(upper: u64) -> u64 {
    (1..upper+1).fold(0, |acc, x| acc + x.pow(2))
}

pub fn difference (upper: u64) -> u64 {
    square_of_sum(upper) - sum_of_squares(upper)
}
