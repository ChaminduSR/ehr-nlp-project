import spacy

nlp = spacy.load("en_core_web_sm")

clinical_note = 

doc = nlp(clinical_note)

print("Clinical Note:")
print(clinical_note)
print("\n" + "=" * 60)

print("\nEntities Found by spaCy:")
print("-" * 60)

if doc.ents:
    for ent in doc.ents:
        print(
            f"Text: {ent.text:30} | Type: {ent.label_:10} | Position: {ent.start_char}-{ent.end_char}"
        )
else:
    print("No entities found.")

print("\n" + "=" * 60)
print("\nEntity Type Breakdown:")
print("-" * 60)

entity_types = {}
for ent in doc.ents:
    if ent.label_ not in entity_types:
        entity_types[ent.label_] = []
    entity_types[ent.label_].append(ent.text)

for ent_type, entities in entity_types.items():
    print(f"\n{ent_type}:")
    for entity in entities:
        print(f"  - {entity}")