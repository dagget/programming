#[derive(Debug, PartialEq, Clone, Copy)]
pub enum Allergen {
    Eggs         = 1,
    Peanuts      = 2,
    Shellfish    = 4,
    Strawberries = 8,
    Tomatoes     = 16,
    Chocolate    = 32,
    Pollen       = 64,
    Cats         = 128,
}

static ALLERGIES: [Allergen; 8] = [
    Allergen::Eggs,
    Allergen::Peanuts,
    Allergen::Shellfish,
    Allergen::Strawberries,
    Allergen::Tomatoes,
    Allergen::Chocolate,
    Allergen::Pollen,
    Allergen::Cats
];

pub struct Allergies(pub u32);

impl Allergies {

    pub fn is_allergic_to(&self, allergen: &Allergen) -> bool {
        (allergen.clone() as u32 & self.0) > 0
    }

    pub fn allergies(&self) -> Vec<Allergen> {
        ALLERGIES.iter().filter(|x| self.is_allergic_to(&x)).cloned().collect::<Vec<_>>()
    }
}
