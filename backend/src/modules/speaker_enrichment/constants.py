class TokenKeys:
    UPOS = "upos"
    FEATS = "feats"
    HEAD = "head"
    ID = "id"
    DEPREL = "deprel"


class Upos:
    VERB = "VERB"
    PRON = "PRON"
    ADJ = "ADJ"  # adjective
    NOUN = "NOUN"


class FeatKeys:
    TENSE = "Tense"
    PERSON = "Person"
    GENDER = "Gender"
    NUMBER = "Number"
    CASE = "Case"


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

    # cases
    LOC = "Loc"  # locative case
    NOM = "Nom"  # nominative case
    INS = "Ins"  # instrumental case  (орудний)
    GEN = "Gen"  # genitive case (родовий)


class Deprel:
    NSUBJ = "nsubj"
    CASE = "case"
