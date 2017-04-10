pub fn raindrops(input: u64) -> String {
    let mut s = "".to_string();

    if input % 3 == 0 { s.push_str("Pling") };
    if input % 5 == 0 { s.push_str("Plang") };
    if input % 7 == 0 { s.push_str("Plong") };
    if s.is_empty()  { s.push_str(&input.to_string()) };

    return s;
}
