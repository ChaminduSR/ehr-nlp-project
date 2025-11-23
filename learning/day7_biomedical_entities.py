import spacy
from collections import Counter

print("="*80)
print("DAY 7: BIOMEDICAL ENTITY RECOGNITION")
print("="*80)

# Load biomedical model
print("\nLoading biomedical model...")
nlp = spacy.load("en_core_sci_sm")
print("✓ Model loaded successfully!")

print("\n\nPart 1: Basic Biomedical Entity Extraction")
print("-"*80)

clinical_note = """
Patient is a 45-year-old male presenting with acute dyspnea and chest pain.
Medical history includes type 2 diabetes mellitus, hypertension, and hyperlipidemia.
Current medications: metformin 1000mg, lisinopril 10mg, atorvastatin 40mg.
Physical exam reveals tachycardia and bilateral pulmonary crackles.
Labs show elevated troponin and BNP. ECG demonstrates ST elevation.
Assessment: acute myocardial infarction with heart failure.
Plan: Start heparin, aspirin, and nitroglycerin. Transfer to cardiac catheterization lab.
"""

print(f"\nClinical Note:\n{clinical_note}")

doc = nlp(clinical_note)

print("\n\nExtracted Entities:")
print("-"*80)
print(f"{'Entity Text':<35} {'Entity Type':<15} {'Start':<8} {'End':<8}")
print("-"*80)

if doc.ents:
    for ent in doc.ents:
        print(f"{ent.text:<35} {ent.label_:<15} {ent.start_char:<8} {ent.end_char:<8}")
else:
    print("No entities found")

print("\n\nPart 2: Entity Type Statistics")
print("-"*80)

# Count entities by type
entity_counts = Counter([ent.label_ for ent in doc.ents])

print("\nEntity Type Distribution:")
for ent_type, count in entity_counts.most_common():
    print(f"  {ent_type:<15} : {count:>3} entities")

print(f"\nTotal entities found: {len(doc.ents)}")

print("\n\nPart 3: Group Entities by Type")
print("-"*80)

# Organize entities by type
entities_by_type = {}
for ent in doc.ents:
    if ent.label_ not in entities_by_type:
        entities_by_type[ent.label_] = []
    entities_by_type[ent.label_].append(ent.text)

# Print grouped entities
for ent_type, entities in sorted(entities_by_type.items()):
    print(f"\n{ent_type}:")
    for entity in set(entities):  # Use set to remove duplicates
        count = entities.count(entity)
        print(f"  - {entity} ({count}x)" if count > 1 else f"  - {entity}")

print("\n\nPart 4: Multiple Clinical Notes Analysis")
print("-"*80)

clinical_notes = [
    "Patient with CAD s/p CABG presents with recurrent angina.",
    "COPD exacerbation, started on prednisone and azithromycin.",
    "CKD stage 3, anemia likely secondary to erythropoietin deficiency.",
    "New diagnosis of breast adenocarcinoma, ER+ PR+ HER2-.",
]

print("\nProcessing multiple clinical notes:\n")

all_entities = []
for note_num, note in enumerate(clinical_notes, 1):
    doc = nlp(note)
    print(f"Note {note_num}: {note}")
    
    if doc.ents:
        print("  Entities:")
        for ent in doc.ents:
            print(f"    - {ent.text} [{ent.label_}]")
            all_entities.append((ent.text, ent.label_))
    else:
        print("  No entities found")
    print()

print("-"*80)
print(f"Total entities across all notes: {len(all_entities)}")

# Count entity types across all notes
all_entity_types = Counter([label for _, label in all_entities])
print("\nEntity type distribution across all notes:")
for ent_type, count in all_entity_types.most_common():
    print(f"  {ent_type:<15} : {count:>3}")

print("\n\nPart 5: Extract Specific Entity Types")
print("-"*80)

sample_text = """
Patient started on lisinopril for hypertension, metformin for diabetes,
and atorvastatin for hyperlipidemia. Lab work shows elevated HbA1c,
low HDL cholesterol, and microalbuminuria. Chest X-ray reveals cardiomegaly.
"""

doc = nlp(sample_text)

# Separate entities by type
diseases = [ent.text for ent in doc.ents if ent.label_ == "DISEASE"]
chemicals = [ent.text for ent in doc.ents if ent.label_ == "CHEMICAL"]

print(f"\nText: {sample_text}\n")
print("DISEASES found:")
for disease in diseases:
    print(f"  - {disease}")

print("\nCHEMICALS/MEDICATIONS found:")
for chemical in chemicals:
    print(f"  - {chemical}")

print("\n\nPart 6: Entity Context (Sentences)")
print("-"*80)

context_text = """
The patient denies chest pain. History of myocardial infarction in 2020.
Currently asymptomatic. No shortness of breath or palpitations.
"""

doc = nlp(context_text)

print(f"\nText: {context_text}\n")
print("Entities with sentence context:")

for ent in doc.ents:
    # Find which sentence contains this entity
    for sent in doc.sents:
        if ent.start >= sent.start and ent.end <= sent.end:
            print(f"\nEntity: {ent.text} [{ent.label_}]")
            print(f"Context: {sent.text.strip()}")
            break

print("\n" + "="*80)
print("ENTITY TYPES IN SCISPACY")
print("="*80)

entity_types_info = """
Common entity types in scispaCy biomedical models:

1. DISEASE
   - Medical conditions, symptoms, syndromes
   - Examples: diabetes, hypertension, pneumonia, dyspnea

2. CHEMICAL
   - Medications, drugs, compounds
   - Examples: metformin, aspirin, insulin, glucose

3. GENE
   - Genetic markers, gene names
   - Examples: BRCA1, TP53, HER2

4. ANATOMY
   - Body parts, organs, anatomical structures
   - Examples: heart, lung, liver, cardiac

Note: The specific entity types available depend on which scispaCy model
you're using. en_core_sci_sm primarily recognizes entities but doesn't
classify them into detailed categories. For more detailed entity typing,
use specialized NER models or entity linkers (covered in later days).
"""

print(entity_types_info)
