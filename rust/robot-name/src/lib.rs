extern crate rand;

use rand::Rng;


pub struct Robot{
    name : String,
}

impl Robot {
    pub fn new() -> Robot {
        let mut r = Robot {
            name: String::new(),
        };
        r.reset_name();
        r
    }

    pub fn name(&self) -> &str {
        &self.name
    }

    pub fn reset_name(&mut self) {
        const CHARSET: &[u8] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        const NUMSET: &[u8] = b"0123456789";

        let mut rng = rand::thread_rng();

        let letters: String = (0..2)
            .map(|_| {
                let idx = rng.gen_range(0, CHARSET.len());
                CHARSET[idx] as char
            })
        .collect();

        let numbers: String = (0..3)
            .map(|_| {
                let idx = rng.gen_range(0, NUMSET.len());
                NUMSET[idx] as char
            })
        .collect();

        self.name = letters + &numbers;
    }
}
