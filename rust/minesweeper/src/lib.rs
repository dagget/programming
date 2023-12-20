pub fn annotate(minefield: &[&str]) -> Vec<String> {
    if minefield.is_empty() { return vec![]; }
    if minefield[0].is_empty() { return vec![String::from("")]; }

    let mut board = vec![];

    for row in 0..minefield.len() {
        let mut line: String = String::new();
        for column in 0..minefield[row].as_bytes().len() {
           println!("--{:?}-- row i {} l{} col i {} l {}", minefield[row].as_bytes(), row, minefield.len(), column, minefield[row].as_bytes().len());
           let mut num = 0;
           // if field is empty, check surroundings to see if a number needs to be in
           if minefield[row].as_bytes()[column] == 32 { 
               if row > 0 && column > 0 && minefield[row-1].as_bytes()[column-1] == 42 { num+=1; }; // top left
               if row > 0 && minefield[row-1].as_bytes()[column] == 42 { num+=1; };// top middle
               if row > 0 && column < minefield[row].len()-1 && minefield[row-1].as_bytes()[column+1] == 42 { num+=1; };// top right
                                                                                                                      
               if column > 0 && minefield[row].as_bytes()[column-1] == 42   { num+=1; }; // left
               if column < minefield[row].len()-1 && minefield[row].as_bytes()[column+1] == 42   { num+=1; }; // right
                                                                          
               if row < minefield.len()-1 && column > 0 && minefield[row+1].as_bytes()[column-1] == 42 { num+=1; }; // bottom left
               if row < minefield.len()-1 && minefield[row+1].as_bytes()[column] == 42   { num+=1; }; // bottom middle
               if row < minefield.len()-1 && column < minefield[row].len()-1 && minefield[row+1].as_bytes()[column+1] == 42 { num+=1; }; // bottom right
                                                                        
               if num > 0 { line.push_str(&num.to_string()) } else { line.push(' ') }
           }
                                                                    
           if minefield[row].as_bytes()[column] == 42 { line.push('*') } // mine 
        }
        board.push(line);
    }
    println!("{:?}", board);
    return board
}
