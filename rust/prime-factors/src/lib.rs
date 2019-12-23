
fn is_divisable_by_2(n: u64) -> bool {
    n & 0x1 == 0
}

fn is_divisible_by_3(n: u64) -> bool {
    let mut sum: u64 = 0;
    let mut rem = n;
    
    while rem > 0 {
        sum += rem % 10;
        rem /= 10;
    }
    sum % 3 == 0
}

fn is_divisible_by_5(n: u64) -> bool {
    let last_digit = n % 10;
    last_digit == 5 || last_digit == 0
}

fn is_divisible_by_7(n: u64) -> bool {
    let last_digit = n % 10;
    let other_digits = n/10;

    other_digits.checked_sub(last_digit * 2).unwrap_or(n) % 7 == 0
}

fn is_prime(n: u64) -> bool {
     for i in 2 .. n/2 {
         if n % i == 0 {
             return false;
         }
     }
     true
}

pub fn factors(n: u64) -> Vec<u64> {
    let mut factors : Vec<u64> = vec![];
    let mut remainder: u64 = n;

    while remainder > 1 {
        if is_divisable_by_2(remainder) {
            factors.push(2);
            remainder /= 2;
            continue;
        }
        if is_divisible_by_3(remainder) {
            factors.push(3);
            remainder /= 3;
            continue;
        }
        if is_divisible_by_5(remainder){
            factors.push(5);
            remainder /= 5;
            continue;
        }
        if is_divisible_by_7(remainder) {
            factors.push(7);
            remainder /= 7;
            continue;
        }

        if is_prime(remainder) {
            factors.push(remainder);
            break;
        }

        // no divisibility rule available
        // use brute force
        for divisor in 11 ..= remainder/2 {
            if is_prime(divisor){
                if remainder % divisor == 0 {
                    factors.push(divisor);
                    remainder /= divisor;
                    break;
                }
            }
        }
    }

    factors.sort();
    factors
}
