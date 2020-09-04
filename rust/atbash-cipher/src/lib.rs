const ALPHABET: [char; 26] = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
    't', 'u', 'v', 'w', 'x', 'y', 'z',
];
const SZ: usize = ALPHABET.len() - 1;

/// "Encipher" with the Atbash cipher.
pub fn encode(plain: &str) -> String {
    let mut i = 0;

    decode(&plain.to_lowercase())
        .chars()
        .filter(|&x| x != '.' && x != ',')
        .fold(String::new(), |mut encoded, x| {
            if i == 5 {
                encoded.push(' ');
                i = 0;
            }
            encoded.push(x);
            i += 1;
            encoded
        })
}

/// "Decipher" with the Atbash cipher.
pub fn decode(cipher: &str) -> String {
    cipher
        .chars()
        .filter(|&x| !x.is_whitespace())
        .map(|x| {
            if let Some(i) = ALPHABET.iter().position(|c| *c == x) {
                ALPHABET[SZ - i]
            } else {
                x
            }
        })
        .collect::<String>()
}
