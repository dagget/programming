extern crate clap;

//use std::env;
//use std::io;
//use std::fs::{self, DirEntry};
use std::fs;
use std::path::Path;
use clap::{Arg, App};

//fn collect_files(input: &str) -> Vec<&std::path::Path> {
fn collect_files(input: &str) {
    let paths = fs::read_dir(Path::new(input));

	//let dir = Path::new(input);
	//let mut result = Vec::<&std::path::Path>::new();

	//if dir.is_dir() {
	//	result.push(dir)
	//} else {
	//	result.push(dir)
	//}

	//result.clone()
}

fn main() {
	let matches = App::new("scanner")
		.author("Micha Hergarden")
		.about("My first rust app - a scanner/lexer")
		.arg(Arg::with_name("SCANDIR")
			.short("d")
			.long("directory")
			.help("The directory to scan")
			.takes_value(true)
			.required(true))
		.get_matches();

	let scandirectory = matches.value_of("SCANDIR").unwrap();
	println!("start scan");
	println!("using directory: {}", scandirectory);
	collect_files(&scandirectory);

	std::process::exit(0);
}
