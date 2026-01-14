class TokenKeys:
    UPOS = "upos"
    FEATS = "feats"
    HEAD = "head"
    ID = "id"
    DEPREL = "deprel"


class Upos:
    VERB = "VERB"
    PRON = "PRON"


class FeatKeys:
    TENSE = "Tense"
    PERSON = "Person"
    GENDER = "Gender"
    NUMBER = "Number"


class FeatValues:
    PAST = "Past"
    PRES = "Pres"

    # person
    FIRST = "1"
    SECOND = "2"
    THIRD = "3"

    # gender
    MASC = "Masc"
    FEM = "Fem"

    # number
    SING = "Sing"

class Deprel:
    NSUBJ = "nsubj"
