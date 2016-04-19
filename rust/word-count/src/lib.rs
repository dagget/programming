extern crate regex;

use std::collections::HashMap;
use regex::Regex;

pub fn word_count(input: &str)  -> HashMap<String, u32> {
    let mut result: HashMap<String, u32> = HashMap::new();
    let re = Regex::new(r"[:^alnum:]").unwrap();

    for word in re.split(input) {
        if word.len() > 0 {
            let counter = result.entry(word.to_lowercase()).or_insert(0);
            *counter += 1;
        }
    }

    result
}
