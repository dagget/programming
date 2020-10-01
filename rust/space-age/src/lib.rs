// The code below is a stub. Just enough to satisfy the compiler.
// In order to pass the tests you can add-to or change any of this code.
const SECONDS_IN_EARTH_YEAR: f64 = (365.25 * 24.0 * 60.0 * 60.0);

#[derive(Debug)]
pub struct Duration {
    earth_years: f64,
}

impl From<u64> for Duration {
    fn from(s: u64) -> Self {
        Duration {
            earth_years: s as f64 / SECONDS_IN_EARTH_YEAR,
        }
    }
}

pub trait Planet {
    const RELATIVE_PERIOD: f64;

    fn years_during(d: &Duration) -> f64 {
        d.earth_years / Self::RELATIVE_PERIOD
    }
}

macro_rules! space_age {
    ($name:ident, $factor:expr) => {
        pub struct $name;
        impl Planet for $name {
            const RELATIVE_PERIOD: f64 = $factor;
        }
    };
}

space_age!(Mercury, 0.240_846_7);
space_age!(Venus, 0.615_197_26);
space_age!(Earth, 1.0);
space_age!(Mars, 1.880_815_8);
space_age!(Jupiter, 11.862_615);
space_age!(Saturn, 29.447_498);
space_age!(Uranus, 84.016_846);
space_age!(Neptune, 164.79132);
