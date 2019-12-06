use std::fmt;
use std::cmp;

#[derive(Debug)]
pub struct Clock{
    hours: i32,
    minutes: i32
}

impl fmt::Display for Clock {
     fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{:02}:{:02}", self.hours, self.minutes)
    }
}

impl cmp::PartialEq for Clock {
    fn eq(&self, other: &Self) -> bool {
        // when comparing, reduce the 'other' clock by removing day overflow
        // and hour overflow
        self.hours == other.hours % 24 && self.minutes == other.minutes % 60
    }
}

impl Clock {
    pub fn new(hours: i32, minutes: i32) -> Self {
        // reduce to minutes for easy removal of day overflow
        let mut tmp: i32 = minutes + (hours * 60);
        let day = 24*60;

        // if negative remove days
        while tmp < -day {
            tmp += day;
        }

        // if positive remove days
        while tmp > day {
            tmp -= day;
        }

        // convert back to hours and minutes
        // rust rounds down in conversion to i32
        let mut h: i32 = tmp/60;
        let mut m: i32 = tmp - (h*60);

        // if time was negative then convert to positive
        h += 24;
        if m < 0 {
            h -= 1;
            m += 60;
        }
        h %= 24;

        Clock {
            hours : h,
            minutes : m
        }
    }

    pub fn add_minutes(&self, minutes: i32) -> Self {
        // convert back to minutes for simple calc
        // m might overflow
        let mut m: i32 = (self.hours * 60) + self.minutes;
        m += minutes;

        let h: i32 = m/60;
        m -= h*60;
        Clock::new(h, m)
    }
}
