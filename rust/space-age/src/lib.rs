// The code below is a stub. Just enough to satisfy the compiler.
// In order to pass the tests you can add-to or change any of this code.

#[derive(Debug)]
pub struct Duration {
    value: u64,
}

impl From<u64> for Duration {
    fn from(s: u64) -> Self {
        Duration { value: s }
    }
}

pub trait Planet {
    fn years_during(d: &Duration) -> f64 {
        unimplemented!(
            "convert a duration ({:?}) to the number of years on this planet for that duration",
            d,
        );
    }
}

pub struct Mercury;
pub struct Venus;
pub struct Earth;
pub struct Mars;
pub struct Jupiter;
pub struct Saturn;
pub struct Uranus;
pub struct Neptune;

impl Planet for Mercury {
    fn years_during(d: &Duration) -> f64 {
        Earth::years_during(d) / 0.240_846_7
    }
}
impl Planet for Venus {
    fn years_during(d: &Duration) -> f64 {
        Earth::years_during(d) / 0.615_197_26
    }
}
impl Planet for Earth {
    fn years_during(d: &Duration) -> f64 {
        d.value as f64 / (365.25 * 24.0 * 60.0 * 60.0)
    }
}
impl Planet for Mars {
    fn years_during(d: &Duration) -> f64 {
        Earth::years_during(d) / 1.880_815_8
    }
}
impl Planet for Jupiter {
    fn years_during(d: &Duration) -> f64 {
        Earth::years_during(d) / 11.862_615
    }
}
impl Planet for Saturn {
    fn years_during(d: &Duration) -> f64 {
        Earth::years_during(d) / 29.447_498
    }
}
impl Planet for Uranus {
    fn years_during(d: &Duration) -> f64 {
        Earth::years_during(d) / 84.016_846
    }
}
impl Planet for Neptune {
    fn years_during(d: &Duration) -> f64 {
        Earth::years_during(d) / 164.79132
    }
}
