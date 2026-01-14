class TokenKeys:
    UPOS = "upos"
    FEATS = "feats"
    HEAD = "head"
    ID = "id"
    DEPREL = "deprel"


class Upos:
    VERB = "VERB"


class FeatKeys:
    TENSE = "Tense"
    PERSON = "Person"
    GENDER = "Gender"


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

class Deprel:
    NSUBJ = "nsubj"
