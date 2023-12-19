#[derive(Debug, PartialEq, Eq)]
pub enum Comparison {
    Equal,
    Sublist,
    Superlist,
    Unequal,
}

pub fn sublist<T: PartialEq>(_first_list: &[T], _second_list: &[T]) -> Comparison {
    let longlist;
    let shortlist;

    if _first_list.len() > _second_list.len() {
        longlist = _first_list;
        shortlist = _second_list;
    } else {
        longlist = _second_list;
        shortlist = _first_list;
    }


    if longlist.len() == 0 && shortlist.len() == 0 { return Comparison::Equal }
    if _first_list.len() == 0 { return Comparison::Sublist } 
    if _second_list.len() == 0 { return Comparison::Superlist }
    if longlist.len() == shortlist.len() && longlist == shortlist { return Comparison::Equal }


    for n in 0..longlist.len() - shortlist.len() + 1 {
        let mut eq = true;

        for (e1, e2) in longlist[n..n+shortlist.len()].iter().zip(shortlist.iter()){
            if e1 != e2 { eq = false; }
        }
        if eq && _first_list.len() > _second_list.len() { return Comparison::Superlist }
        if eq && _first_list.len() < _second_list.len() { return Comparison::Sublist }
    }

    Comparison::Unequal
}
