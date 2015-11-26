extern crate getopts;

use getopts::Options;
use std::env;

use std::io;
use std::fs::{self, DirEntry};
use std::path::Path;

fn collect_files(input: &str){
	println!("using directory: {:?}", input);

	let dir = Path::new(input);

	if try!(fs::metadata(dir)).is_dir() {
		for entry in try!(fs::read_dir(dir)) {
			let entry = try!(entry);
			if try!(fs::metadata(entry.path())).is_dir() {
				//try!(visit_dirs(&entry.path(), cb));
				println!("directory {:?}", entry.path);
			} else {
				println!("file {:?}", entry.path);
			}
		}
	}
	Ok(())
}

fn print_usage(program: &str, opts: Options) {
	let brief = format!("Usage: {} [options]", program);
	print!("{}", opts.usage(&brief));
}


fn main() {
	let args: Vec<String> = env::args().collect();
	let program = args[0].clone();
	let mut opts = Options::new();

	opts.optflag("h", "help", "print help");
	opts.optopt("d", "directory", "the directory containing input files.", "<directory>");

	let matches = match opts.parse(&args[1..]) {
		Ok(m) => { m }
		Err(f) => { panic!(f.to_string()) }
	};
	if matches.opt_present("h") {
		print_usage(&program, opts);
		return;
	}

	let input = matches.opt_str("d");

	println!("start scan");
	collect_files(input);
}
