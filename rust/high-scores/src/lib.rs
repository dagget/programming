#[derive(Debug)]
pub struct HighScores<'a>(&'a [u32]);

impl<'a> HighScores<'a> {
    pub fn new(scores: &'a [u32]) -> Self {
        HighScores(scores)
    }

    pub fn scores(&self) -> &[u32] {
        self.0
    }

    pub fn latest(&self) -> Option<u32> {
        self.0.last().cloned()
    }

    pub fn personal_best(&self) -> Option<u32> {
        let mut y = self.0.to_vec();
        y.sort();
        y.last().cloned()
    }

    pub fn personal_top_three(&self) -> Vec<u32> {
        let mut y = self.0.to_vec();
        y.sort();
        y.reverse();
        if y.len() >= 3 {
            y.split_off(3);
        } 

        y
    }
}
