use std::fmt;

#[derive(Debug,PartialEq)]
pub struct Clock{
    hours: i32,
    minutes: i32
}

impl fmt::Display for Clock {
     fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{:02}:{:02}", self.hours, self.minutes)
    }
}

impl Clock {
    pub fn new(hours: i32, minutes: i32) -> Self {
        // reduce to minutes for easy removal of day overflow
        let mut total_minutes: i32 = minutes + (hours * 60);
        const DAY: i32 = 24*60;

        total_minutes %= DAY;

        // Rust % is the remainder operator, not modulus
        // total_minutes might still be negative.
        while total_minutes < 0 {
            total_minutes += DAY;
        }

        // convert back to hours and minutes
        Clock {
            hours : total_minutes/60,
            // total_minutes/60 rounds down during conversion
            // to i32.
            minutes : total_minutes - ((total_minutes/60)*60)
        }
    }

    pub fn add_minutes(&self, minutes: i32) -> Self {
        Clock::new(self.hours, self.minutes + minutes)
    }
}
