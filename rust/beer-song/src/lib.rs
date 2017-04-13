pub fn verse(start: u64) -> String
{
    let mut verse = String::from("") ;

    match start {
        0 => verse.push_str("No more bottles of beer on the wall, no more bottles of beer.\nGo to the store and buy some more, 99 bottles of beer on the wall.\n"),
        1 => verse.push_str("1 bottle of beer on the wall, 1 bottle of beer.\nTake it down and pass it around, no more bottles of beer on the wall.\n"),
        2 => verse.push_str("2 bottles of beer on the wall, 2 bottles of beer.\nTake one down and pass it around, 1 bottle of beer on the wall.\n"),
        num => verse.push_str(format!("{} bottles of beer on the wall, {} bottles of beer.\nTake one down and pass it around, {} bottles of beer on the wall.\n", num, num, num-1).as_str()),
    }
    return verse
}

pub fn sing(start: u64, end: u64) -> String
{
    if start > end {
        return verse(start) + "\n" + &sing(start - 1, end);
    } else {
        return verse(end)
    }
}
