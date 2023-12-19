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

    if (longlist.is_empty() && shortlist.is_empty()) || (longlist == shortlist) { return Comparison::Equal }
    if _first_list.is_empty() { return Comparison::Sublist } 
    if _second_list.is_empty() { return Comparison::Superlist }

    let eq = longlist.windows(shortlist.len()).any(|x| x == shortlist);
    if eq && _first_list.len() > _second_list.len() { return Comparison::Superlist }
    if eq && _first_list.len() < _second_list.len() { return Comparison::Sublist }

    Comparison::Unequal
}
