# i will be making this customizable soon

class Conditions:
    star_rating = staticmethod(lambda sr: 3.72 < sr < 4.6)
    length_0 = staticmethod(lambda length: length < 62)
    length_4 = staticmethod(lambda length: length < 93)
    rp_0 = staticmethod(lambda rp: rp > 85)
    rp_4 = staticmethod(lambda rp: rp > 118)
    perfect_0 = staticmethod(lambda rp, length: rp > 85 and length < 60)
    perfect_4 = staticmethod(lambda rp, length: rp > 118 and length < 90)