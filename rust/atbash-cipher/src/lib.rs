const ALPHABET : [char;26]  = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'];
const SZ : usize = ALPHABET.len() - 1;

/// "Encipher" with the Atbash cipher.
pub fn encode(plain: &str) -> String {
    let mut encoded = plain.to_lowercase().to_string();
    encoded = encoded.chars().filter(|x| x.is_alphanumeric()).collect();
    encoded = encoded 
             .chars()
             .map(|x| if x.is_alphabetic() { ALPHABET[SZ - ALPHABET
                                        .iter()
                                        .position(|c| *c == x)
                                        .unwrap()]
                                      } else {
                                          x
                                      }
                 )
             .collect::<String>();

    let mut split_encoded = String::new();
    while encoded.len() > 5 {
        split_encoded += &(encoded.drain(..5).collect::<String>() + " ");
    }
    split_encoded + &encoded
}

/// "Decipher" with the Atbash cipher.
pub fn decode(cipher: &str) -> String {
    encode(cipher).chars().filter(|x| x.is_alphanumeric()).collect()
}
