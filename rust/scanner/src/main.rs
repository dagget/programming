extern crate clap;

use std::env;

use std::io;
use std::fs::{self, DirEntry};
use std::path::Path;
use clap::{Arg, App, SubCommand};

fn collect_files(input: &str){
	let dir = Path::new(input);

	if try!(fs::metadata(dir)).is_dir() {
//		for entry in try!(fs::read_dir(dir)) {
//			let entry = try!(entry);
//			if try!(fs::metadata(entry.path())).is_dir() {
//				//try!(visit_dirs(&entry.path(), cb));
//				println!("directory {:?}", entry.path);
//			} else {
//				println!("file {:?}", entry.path);
//			}
//		}
	}
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
}
