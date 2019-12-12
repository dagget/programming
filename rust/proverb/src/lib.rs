pub fn build_proverb(list: &[&str]) -> String {
    match list.len() {
        0 => String::new(),
        1 => format!("And all for the want of a {}.", list[0]),
        _ => {
            let mut s = String::new();
            for i in 0 .. list.len()-1 {
                s = format!("{}For want of a {} the {} was lost.\n", s, list[i], list[i+1])
            }
            format!("{}And all for the want of a {}.", s, list[0])
        }
    }
}
