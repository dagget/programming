pub fn brackets_are_balanced(string: &str) -> bool {
    let mut stack: Vec<char> = vec![];

    let mut result = 
        string
        .chars()
        .map( |x| match x {
            '(' | '{' | '[' => {stack.push(x); true},
            ']' => stack.pop() == Some('['),
            '}' => stack.pop() == Some('{'),
            ')' => stack.pop() == Some('('),
            _ => true,
        })
        .all(|x| x);

    result &= stack.is_empty();
    result
}
