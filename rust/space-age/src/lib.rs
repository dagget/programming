// The code below is a stub. Just enough to satisfy the compiler.
// In order to pass the tests you can add-to or change any of this code.
const SECONDS_IN_EARTH_YEAR: f64=(365.25 * 24.0 * 60.0 * 60.0);

#[derive(Debug)]
pub struct Duration {
    earth_years: f64,
}

impl From<u64> for Duration {
    fn from(s: u64) -> Self {
        Duration { 
            earth_years: s as f64 / SECONDS_IN_EARTH_YEAR
        }
    }
}

pub trait Planet {
    const RELATIVE_PERIOD: f64;

    fn years_during(d: &Duration) -> f64 {
        d.earth_years / Self::RELATIVE_PERIOD
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
        const RELATIVE_PERIOD: f64 = 0.240_846_7;
}
impl Planet for Venus {
        const RELATIVE_PERIOD: f64 = 0.615_197_26;
}
impl Planet for Earth {
        const RELATIVE_PERIOD: f64 = 1.0;
}
impl Planet for Mars {
        const RELATIVE_PERIOD: f64 = 1.880_815_8;
}
impl Planet for Jupiter {
        const RELATIVE_PERIOD: f64 = 11.862_615;
}
impl Planet for Saturn {
        const RELATIVE_PERIOD: f64 = 29.447_498;
}
impl Planet for Uranus {
        const RELATIVE_PERIOD: f64 = 84.016_846;
}
impl Planet for Neptune {
        const RELATIVE_PERIOD: f64 = 164.79132;
}
