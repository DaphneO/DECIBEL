class AlignmentScore(float):
    def __new__(cls, value):
        return super().__new__(cls, value)

    @property
    def is_well_aligned(self):
        return self <= 0.85
