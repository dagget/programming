pub fn anagrams_for<'a>(word: &str, inputs: &[&'a str]) -> Vec<&'a str> {
    let mut output: Vec<&str> = vec![];
    let mut sorted_word: Vec<char> = word.to_lowercase().chars().collect();
    sorted_word.sort();

    for input in inputs {
        if input.to_lowercase() != word.to_lowercase() {
            let mut sorted_input: Vec<char> = input.to_lowercase().chars().collect();
            sorted_input.sort();

            if sorted_word == sorted_input {
                output.push(input);
            }
        }
    }

    output
}
