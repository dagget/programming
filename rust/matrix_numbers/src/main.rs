use std::process;
//use std::io;

const N: usize = 10;

fn print_matrix(matrix: &[[usize; N]; N]){
	println!("");
    for x in 0..N {
        for y in 0..N {
            print!("{number:>width$} ", number=matrix[y][x], width=3);
        }
        println!("")
    }
	println!("");
}

fn fill_matrix(value: usize, x: usize, y: usize, mut matrix: &mut [[usize; N]; N]){
	if value > N*N {
		println!("Found solution");
		print_matrix(&matrix);
        process::exit(0);
	} else {
		matrix[x][y] = value;

		if x.checked_add(3).unwrap_or(N+1) < N && matrix[x+3][y] == 0 { fill_matrix(value+1, x+3, y, &mut matrix) }
		//print_matrix(&matrix);
        //let mut inp = String::new();
        //io::stdin().read_line(&mut inp);

		if x.checked_add(2).unwrap_or(N+1) < N && y.checked_add(2).unwrap_or(N+1) < N && matrix[x+2][y+2] == 0 { fill_matrix(value+1, x+2, y+2, &mut matrix) }
		if y.checked_add(3).unwrap_or(N+1) < N && matrix[x][y+3] == 0 { fill_matrix(value+1, x, y+3, &mut matrix) }
		if x.checked_sub(2).unwrap_or(N+1) < N && y.checked_add(2).unwrap_or(N+1) < N && matrix[x-2][y+2] == 0 { fill_matrix(value+1, x-2, y+2, &mut matrix) }
		if x.checked_sub(3).unwrap_or(N+1) < N && matrix[x-3][y] == 0 { fill_matrix(value+1, x-3, y, &mut matrix) }
		if x.checked_sub(2).unwrap_or(N+1) < N && y.checked_sub(2).unwrap_or(N+1) < N && matrix[x-2][y-2] == 0 { fill_matrix(value+1, x-2, y-2, &mut matrix) }
		if y.checked_sub(3).unwrap_or(N+1) < N && matrix[x][y-3] == 0 { fill_matrix(value+1, x, y-3, &mut matrix) }
		if x.checked_add(2).unwrap_or(N+1) < N && y.checked_sub(2).unwrap_or(N+1) < N && matrix[x+2][y-2] == 0 { fill_matrix(value+1, x+2, y-2, &mut matrix) }

		// At this point there is no solution found and no further moves are possible
		// Revert the value to backtrack
		matrix[x][y] = 0;
	}

}

fn main() {
    let mut matrix: [[usize; N]; N] = [[0; N]; N];
    fill_matrix(1, 0, 0, &mut matrix);
}
