pub fn reply(input: &str) -> &str {
    if input.is_empty() { return "Fine. Be that way!" } 
    else if input.ends_with("?") { return "Sure." }
    else if input.to_uppercase() == input { return "Whoa, chill out!" }
    return "Whatever."
}
