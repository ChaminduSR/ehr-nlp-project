import spacy
import warnings

warnings.filterwarnings('ignore', category=UserWarning)


print("="*80)
print("DAY 9: UMLS ENTITY LINKING")
print("="*80)

print("\nLoading biomedical model...")
nlp = spacy.load("en_core_sci_sm")

print("Adding UMLS entity linker to pipeline...")
print("(First time: This will download the knowledge base ~1GB)")
print("(Subsequent runs: Will load from cache)")

try:
    # Add entity linker with UMLS knowledge base
    nlp.add_pipe("scispacy_linker", config={"resolve_abbreviations": True, "linker_name": "umls"})
    print("✓ Entity linker added successfully!")
except Exception as e:
    print(f"⚠ Error adding linker: {e}")
    print("Note: The knowledge base will download on first use.")

print("\n\nPart 1: Basic UMLS Linking")
print("-"*80)

sample_text = """
Patient diagnosed with type 2 diabetes mellitus and hypertension.
Started on metformin for glucose control.
"""

print(f"Text: {sample_text}\n")

doc = nlp(sample_text)

print("Entities with UMLS CUI Links:")
print(f"{'Entity':<30} {'UMLS CUI':<15} {'Score':<10} {'Definition'}")
print("-"*80)

for ent in doc.ents:
    # Get UMLS links for this entity
    if ent._.kb_ents:
        # Get top linked concept
        umls_cui = ent._.kb_ents[0][0]  # (CUI, score) tuple
        score = ent._.kb_ents[0][1]

        # Get entity linker to access knowledge base
        linker = nlp.get_pipe("scispacy_linker")
        kb = linker.kb

        # Get definition from knowledge base with error handling
        if umls_cui in kb.cui_to_entity:
            entity_obj = kb.cui_to_entity[umls_cui]

            # Safely handle None definition
            if entity_obj.definition:
                definition = entity_obj.definition[:60] + "..." if len(entity_obj.definition) > 60 else entity_obj.definition
            else:
                definition = "No definition available"
        else:
            definition = "CUI not in knowledge base"

        print(f"{ent.text:<30} {umls_cui:<15} {score:<10.3f} {definition}")
    else:
        print(f"{ent.text:<30} {'No CUI found':<15} {'N/A':<10} N/A")

print("\n\nPart 2: Multiple Candidate Links")
print("-"*80)

clinical_text = """
Patient presents with acute myocardial infarction.
History of congestive heart failure and diabetes.
"""

print(f"Text: {clinical_text}\n")

doc = nlp(clinical_text)

print("Entities with Top 3 UMLS Candidates:")
print("-"*80)

for ent in doc.ents:
    print(f"\nEntity: {ent.text}")

    if ent._.kb_ents:
        print("  Top UMLS matches:")

        # Show top 3 candidates
        for cui, score in ent._.kb_ents[:3]:
            linker = nlp.get_pipe("scispacy_linker")
            kb = linker.kb

            if cui in kb.cui_to_entity:
                entity_obj = kb.cui_to_entity[cui]
                canonical_name = entity_obj.canonical_name if entity_obj.canonical_name else "Unknown"

                # Safely handle None definition
                if entity_obj.definition:
                    definition = entity_obj.definition[:50] + "..." if len(entity_obj.definition) > 50 else entity_obj.definition
                else:
                    definition = "No definition available"

                print(f"    CUI: {cui} (score: {score:.3f})")
                print(f"      Name: {canonical_name}")
                print(f"      Def: {definition}")
    else:
        print("  No UMLS links found")

print("\n\nPart 3: Build Concept Dictionary")
print("-"*80)

notes = [
    "Patient with diabetes and hypertension on metformin.",
    "History of myocardial infarction, started on aspirin.",
    "COPD exacerbation treated with steroids.",
]

print("Processing multiple notes to extract concepts:\n")

# Dictionary to store entity -> CUI mappings
entity_to_cui = {}
cui_to_info = {}

for note_num, note in enumerate(notes, 1):
    doc = nlp(note)
    print(f"Note {note_num}: {note}")
    print("  Concepts:")

    for ent in doc.ents:
        if ent._.kb_ents:
            top_cui = ent._.kb_ents[0][0]
            entity_to_cui[ent.text] = top_cui

            # Store CUI information
            if top_cui not in cui_to_info:
                linker = nlp.get_pipe("scispacy_linker")
                kb = linker.kb

                if top_cui in kb.cui_to_entity:
                    cui_obj = kb.cui_to_entity[top_cui]
                    cui_to_info[top_cui] = {
                        'canonical_name': cui_obj.canonical_name if cui_obj.canonical_name else "Unknown",
                        'definition': cui_obj.definition if cui_obj.definition else "No definition",
                        'aliases': cui_obj.aliases[:3] if cui_obj.aliases else []
                    }

            print(f"    - {ent.text} → {top_cui}")
    print()

print("-"*80)
print(f"\nExtracted {len(entity_to_cui)} unique entity mappings")
print(f"Found {len(cui_to_info)} unique UMLS concepts\n")

print("Concept Information:")
for cui, info in list(cui_to_info.items())[:5]:  # Show first 5
    print(f"\nCUI: {cui}")
    print(f"  Canonical Name: {info['canonical_name']}")
    print(f"  Definition: {info['definition'][:70]}..." if len(info['definition']) > 70 else f"  Definition: {info['definition']}")
    if info['aliases']:
        print(f"  Aliases: {', '.join(info['aliases'][:3])}")

print("\n\nPart 4: Normalize Terminology")
print("-"*80)

# Different ways to express same concept
variations_text = """
Patient 1: diagnosed with diabetes mellitus type 2.
Patient 2: has type 2 diabetes.
Patient 3: type 2 diabetes confirmed.
"""

print(f"Text with variations: {variations_text}\n")

doc = nlp(variations_text)

print("All variations should link to same UMLS concept:")
diabetes_entities = []

for ent in doc.ents:
    # Filter for diabetes-related entities
    if 'diabet' in ent.text.lower():
        if ent._.kb_ents:
            cui = ent._.kb_ents[0][0]
            score = ent._.kb_ents[0][1]
            diabetes_entities.append((ent.text, cui, score))

if diabetes_entities:
    print(f"{'Text Variant':<40} {'UMLS CUI':<15} {'Score':<10}")
    print("-"*80)
    for text, cui, score in diabetes_entities:
        print(f"{text:<40} {cui:<15} {score:<10.3f}")

    # Check if they normalize to same concept
    unique_cuis = set([cui for _, cui, _ in diabetes_entities])
    print(f"\nUnique UMLS concepts: {len(unique_cuis)}")
    if len(unique_cuis) == 1:
        print("✓ All variations successfully normalized to same concept!")
    else:
        print(f"Found {len(unique_cuis)} different concepts")
else:
    print("No diabetes entities detected for comparison")

print("\n\nPart 5: Entity Linking Statistics")
print("-"*80)

stats_text = """
Patient history includes coronary artery disease, myocardial infarction,
congestive heart failure, chronic kidney disease, and diabetes mellitus.
Medications: aspirin, metformin, lisinopril, atorvastatin.
"""

print(f"Text: {stats_text}\n")

doc = nlp(stats_text)

total_entities = len(doc.ents)
linked_entities = sum(1 for ent in doc.ents if ent._.kb_ents)
unlinked_entities = total_entities - linked_entities

print("Entity Linking Statistics:")
print(f"  Total entities: {total_entities}")
print(f"  Successfully linked: {linked_entities}")
print(f"  Not linked: {unlinked_entities}")

if total_entities > 0:
    print(f"  Link success rate: {(linked_entities/total_entities)*100:.1f}%")

# Calculate average scores
all_scores = []
for ent in doc.ents:
    if ent._.kb_ents:
        all_scores.append(ent._.kb_ents[0][1])

if all_scores:
    avg_score = sum(all_scores) / len(all_scores)
    print(f"  Average linking confidence: {avg_score:.3f}")

print("\n\nPart 6: Save Mappings for Reuse")
print("-"*80)

import json

# Save entity-to-CUI mappings
output_file = "entity_cui_mappings.json"

mappings = {}
sample_notes = [
    "Patient with diabetes, hypertension, and heart failure.",
    "Medications include metformin, lisinopril, and aspirin.",
]

for note in sample_notes:
    doc = nlp(note)
    for ent in doc.ents:
        if ent._.kb_ents:
            cui = ent._.kb_ents[0][0]
            score = ent._.kb_ents[0][1]

            if ent.text not in mappings:
                mappings[ent.text] = {
                    'cui': cui,
                    'score': float(score),
                    'occurrences': 1
                }
            else:
                mappings[ent.text]['occurrences'] += 1

# Save to JSON
with open(output_file, 'w') as f:
    json.dump(mappings, f, indent=2)

print(f"Saved {len(mappings)} entity-to-CUI mappings to {output_file}")
print("\nSample mappings:")
for entity, info in list(mappings.items())[:5]:
    print(f"  {entity}: {info['cui']} (score: {info['score']:.3f}, seen {info['occurrences']}x)")

print("\n" + "="*80)
print("UNDERSTANDING UMLS")
print("="*80)

umls_explanation = """
UMLS (Unified Medical Language System) is a comprehensive knowledge base
that integrates medical terminology from multiple sources:

1. CONCEPT UNIQUE IDENTIFIERS (CUIs)
   - Format: C followed by 7 digits (e.g., C0011849)
   - Each CUI represents a unique medical concept
   - Links different terms that mean the same thing

2. WHY UMLS MATTERS
   - "Diabetes", "DM", "diabetes mellitus" → SAME CUI
   - Enables terminology normalization
   - Connects to medical knowledge bases
   - Essential for healthcare interoperability

3. ENTITY LINKING PROCESS
   a. Extract entity from text ("diabetes")
   b. Generate candidates from knowledge base
   c. Score each candidate
   d. Select best match (highest score)
   e. Return CUI (e.g., C0011849)

4. LINKING SCORES
   - Range: 0.0 to 1.0
   - Higher = better match
   - Typically: >0.8 is good, >0.9 is excellent
   - Based on string similarity and context
"""

print(umls_explanation)

print("\n" + "="*80)
print("COMMON UMLS CUIs REFERENCE")
print("="*80)

common_cuis = {
    "C0011849": "Diabetes Mellitus",
    "C0020538": "Hypertension",
    "C0018802": "Congestive Heart Failure",
    "C0027051": "Myocardial Infarction",
    "C0010054": "Coronary Artery Disease",
    "C0024117": "Chronic Obstructive Pulmonary Disease",
    "C0004057": "Aspirin",
    "C0025598": "Metformin",
}

print("\nFrequently Used Medical Concept CUIs:\n")
for cui, name in common_cuis.items():
    print(f"  {cui:<12} = {name}")

print("\n✓ Day 9 Complete!")
