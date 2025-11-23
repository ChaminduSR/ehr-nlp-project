import spacy

nlp = spacy.load("en_core_web_sm")

clinical_notes = [
    "Patient takes metformin daily.",
    "Doctor prescribed antibiotics for infection.",
    "No allergies reported.",
]

print("=" * 80)
print("DEPENDENCY PARSING ANALYSIS")
print("=" * 80)

for note_num, note in enumerate(clinical_notes, 1):
    doc = nlp(note)

    print(f"\n\nNote {note_num}: {note}")
    print("-" * 80)

    print("\nToken Dependencies:")
    print(f"{'Token':<15} {'Pos':<10} {'Dependency':<15} {'Head':<15}")
    print("-" * 80)

    for token in doc:
        print(
            f"{token.text:<15} {token.pos_:<10} {token.dep_:<15} {token.head.text:<15}"
        )

    print("\n\nDependency Tree (Visual):")
    print("-" * 80)

    for token in doc:
        indent = "  " * (len([t for t in token.ancestors]))  # noqa: C416
        dep_type = token.dep_
        parent = token.head.text
        print(f"{indent}{token.text:15} ({dep_type:12}) -> {parent}")

    print("\n\nToken-Head Relationships:")
    print("-" * 80)

    for token in doc:
        if token.dep_ != "ROOT":
            relationship = f"{token.text} --{token.dep_}--> {token.head.text}"
            print(f"  {relationship}")

    print("\n")

print("\n" + "=" * 80)
print("KEY DEPENDENCY TYPES:")
print("=" * 80)

dependency_guide = {
    "nsubj": "Nominal subject (who/what does the action)",
    "dobj": "Direct object (what receives the action)",
    "iobj": "Indirect object (to/for whom)",
    "ROOT": "The main verb of the sentence",
    "prep": "Preposition (in, on, at, by, etc.)",
    "advmod": "Adverbial modifier (how, when, where)",
    "amod": "Adjectival modifier (descriptive word)",
    "det": "Determiner (the, a, this, that)",
    "pobj": "Object of preposition (follows a preposition)",
    "conj": "Conjunction (and, or, but connecting words)",
}

for dep_type, description in dependency_guide.items():
    print(f"  {dep_type:<12} = {description}")
