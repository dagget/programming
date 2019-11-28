const N: usize = 10;

fn print_matrix(matrix: &[[usize; N]; N]) {
    println!("");
    for x in 0..N {
        for y in 0..N {
            print!("{number:>width$} ", number = matrix[y][x], width = 3);
        }
        println!("")
    }
    println!("");
}

fn fill_matrix(value: usize, x: usize, y: usize, mut matrix: &mut [[usize; N]; N]) {
    if value > N * N {
        println!("Found solution");
        print_matrix(&matrix);
    } else {
        matrix[x][y] = value;

        if x < N - 3 && matrix[x + 3][y] == 0                  { fill_matrix(value + 1, x + 3, y    , &mut matrix) }
        if x < N - 2 && y < N - 2 && matrix[x + 2][y + 2] == 0 { fill_matrix(value + 1, x + 2, y + 2, &mut matrix) }
        if y < N - 3 && matrix[x][y + 3] == 0                  { fill_matrix(value + 1, x    , y + 3, &mut matrix) }
        if x > 2 && y < N - 2 && matrix[x - 2][y + 2] == 0     { fill_matrix(value + 1, x - 2, y + 2, &mut matrix) }
        if x > 3 && matrix[x - 3][y] == 0                      { fill_matrix(value + 1, x - 3, y    , &mut matrix) }
        if x > 2 && y > 2 && matrix[x - 2][y - 2] == 0         { fill_matrix(value + 1, x - 2, y - 2, &mut matrix) }
        if y > 3 && matrix[x][y - 3] == 0                      { fill_matrix(value + 1, x    , y - 3, &mut matrix) }
        if x < N - 2 && y > 2 && matrix[x + 2][y - 2] == 0     { fill_matrix(value + 1, x + 2, y - 2, &mut matrix) }

        // At this point there is no solution found and no further moves are possible
        // Revert the value to backtrack
        matrix[x][y] = 0;
    }

}

fn main() {
    let mut matrix: [[usize; N]; N] = [[0; N]; N];

    fill_matrix(1, 0, 0, &mut matrix);
}
