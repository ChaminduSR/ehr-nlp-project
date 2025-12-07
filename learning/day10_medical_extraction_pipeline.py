import spacy
import json
import warnings
from collections import Counter, defaultdict

# Suppress version warnings
warnings.filterwarnings('ignore', category=UserWarning)

print("="*80)
print("DAY 10: COMPLETE MEDICAL EXTRACTION PIPELINE")
print("="*80)

print("\n🔧 Building NLP Pipeline...")
print("-"*80)

# Load biomedical model
print("1. Loading biomedical model...")
nlp = spacy.load("en_core_sci_sm")
print("   ✓ Biomedical model loaded")

# Add abbreviation detector
print("2. Adding abbreviation detector...")
nlp.add_pipe("abbreviation_detector")
print("   ✓ Abbreviation detector added")

# Add entity linker
print("3. Adding UMLS entity linker...")
try:
    nlp.add_pipe("scispacy_linker", config={"resolve_abbreviations": True, "linker_name": "umls"})
    print("   ✓ UMLS entity linker added")
except Exception as e:
    print(f"   ⚠ Entity linker note: {e}")

print("\n✓ Pipeline ready with 3 components!")
print("  - Biomedical NER")
print("  - Abbreviation Detection")
print("  - UMLS Entity Linking")

# ============================================================================
# PART 1: Process Single Clinical Note
# ============================================================================

print("\n\n" + "="*80)
print("PART 1: COMPLETE EXTRACTION FROM SINGLE NOTE")
print("="*80)

clinical_note = """
PATIENT: John Doe, 67 y/o M
CC: Chest pain and shortness of breath

HPI: Patient with history of coronary artery disease (CAD) s/p CABG in 2018
presents to ED with acute onset chest pain radiating to left arm. Associated
with dyspnea and diaphoresis. Denies nausea or vomiting.

PMH:
- Type 2 diabetes mellitus (DM2) - diagnosed 2015
- Hypertension (HTN) - on medications
- Hyperlipidemia - well controlled
- Chronic kidney disease (CKD) stage 3

MEDICATIONS:
- Metformin 1000mg PO BID
- Lisinopril 10mg PO daily
- Atorvastatin 40mg PO HS
- Aspirin (ASA) 81mg PO daily

PHYSICAL EXAM:
VS: BP 165/95, HR 110, RR 24, O2 sat 88% on RA
Gen: Anxious, diaphoretic
CV: Tachycardic, regular rhythm, no murmurs
Resp: Bilateral crackles, decreased breath sounds at bases

LABS:
- Troponin: 2.5 (elevated)
- BNP: 850 (elevated)
- BUN/Cr: 45/2.1 (elevated)
- HbA1c: 8.2% (poor control)

IMAGING:
- ECG: ST elevation in leads II, III, aVF
- CXR: Cardiomegaly, pulmonary edema

ASSESSMENT:
1. Acute ST-elevation myocardial infarction (STEMI)
2. Acute decompensated heart failure (ADHF)
3. Acute kidney injury (AKI) on CKD

PLAN:
- Transfer to cardiac catheterization lab for emergent PCI
- Start heparin, nitroglycerin drips
- Consult cardiology and nephrology
- ICU admission
"""

print(f"\nClinical Note Length: {len(clinical_note)} characters")
print(f"\nProcessing note...\n")

doc = nlp(clinical_note)

# Extract all entities
print("\n1️⃣  ENTITY EXTRACTION")
print("-"*80)
print(f"{'Entity':<40} {'Type':<15} {'Position'}")
print("-"*80)

entities = []
for ent in doc.ents[:15]:  # Show first 15
    print(f"{ent.text:<40} {ent.label_:<15} {ent.start_char:>4}-{ent.end_char:<4}")
    entities.append({'text': ent.text, 'type': ent.label_, 'start': ent.start_char, 'end': ent.end_char})

print(f"\n   Total entities found: {len(doc.ents)}")

# Extract abbreviations
print("\n\n2️⃣  ABBREVIATION DETECTION")
print("-"*80)
print(f"{'Abbreviation':<20} {'Long Form':<50}")
print("-"*80)

abbreviations = []
if doc._.abbreviations:
    for abbr in doc._.abbreviations[:10]:  # Show first 10
        short = str(abbr)
        long = str(abbr._.long_form)
        print(f"{short:<20} {long:<50}")
        abbreviations.append({'short': short, 'long': long})
    print(f"\n   Total abbreviations detected: {len(doc._.abbreviations)}")
else:
    print("   No abbreviations detected")

# Link to UMLS
print("\n\n3️⃣  UMLS CONCEPT LINKING")
print("-"*80)
print(f"{'Entity':<35} {'UMLS CUI':<15} {'Score':<8} {'Concept Name'}")
print("-"*80)

umls_links = []
linked_count = 0

for ent in doc.ents[:15]:  # Show first 15
    if ent._.kb_ents:
        linked_count += 1
        cui = ent._.kb_ents[0][0]
        score = ent._.kb_ents[0][1]

        linker = nlp.get_pipe("scispacy_linker")
        kb = linker.kb

        if cui in kb.cui_to_entity:
            concept_name = kb.cui_to_entity[cui].canonical_name
            if concept_name:
                concept_name = concept_name[:30]
            else:
                concept_name = "N/A"
        else:
            concept_name = "N/A"

        print(f"{ent.text:<35} {cui:<15} {score:<8.3f} {concept_name}")
        umls_links.append({'entity': ent.text, 'cui': cui, 'score': score, 'concept': concept_name})

print(f"\n   Entities linked: {linked_count}/{len(doc.ents)} ({linked_count/len(doc.ents)*100:.1f}%)")

# ============================================================================
# PART 2: Extract Structured Information
# ============================================================================

print("\n\n" + "="*80)
print("PART 2: STRUCTURED INFORMATION EXTRACTION")
print("="*80)

# Group entities by type
entities_by_type = defaultdict(list)
for ent in doc.ents:
    entities_by_type[ent.label_].append(ent.text)

print("\n📊 Entities Grouped by Type:")
print("-"*80)

for ent_type, ents in sorted(entities_by_type.items()):
    unique_ents = list(set(ents))[:5]  # First 5 unique
    count = len(ents)
    print(f"\n{ent_type} ({count} total):")
    for ent in unique_ents:
        print(f"  - {ent}")

# Extract diseases
print("\n\n🏥 DISEASES & CONDITIONS:")
print("-"*80)
diseases = [ent.text for ent in doc.ents if ent.label_ == "DISEASE"]
unique_diseases = list(set(diseases))
for i, disease in enumerate(unique_diseases[:10], 1):
    print(f"{i}. {disease}")

# Extract medications
print("\n\n💊 MEDICATIONS:")
print("-"*80)
medications = [ent.text for ent in doc.ents if ent.label_ == "CHEMICAL"]
unique_meds = list(set(medications))
for i, med in enumerate(unique_meds[:10], 1):
    print(f"{i}. {med}")

# ============================================================================
# PART 3: Build Knowledge Base
# ============================================================================

print("\n\n" + "="*80)
print("PART 3: BUILD MEDICAL KNOWLEDGE BASE")
print("="*80)

knowledge_base = {
    'patient_id': 'P001',
    'note_id': 'N001',
    'note_length': len(clinical_note),
    'entities': {
        'total': len(doc.ents),
        'by_type': {k: len(v) for k, v in entities_by_type.items()},
        'diseases': unique_diseases[:10],
        'medications': unique_meds[:10],
    },
    'abbreviations': abbreviations,
    'umls_concepts': umls_links[:10],
    'statistics': {
        'abbreviations_count': len(doc._.abbreviations) if doc._.abbreviations else 0,
        'linked_entities': linked_count,
        'link_rate': f"{linked_count/len(doc.ents)*100:.1f}%"
    }
}

print("\n📚 Knowledge Base Structure:")
print(json.dumps(knowledge_base, indent=2)[:800] + "\n...")

# Save to file
output_file = "patient_knowledge_base.json"
with open(output_file, 'w') as f:
    json.dump(knowledge_base, f, indent=2)

print(f"\n✓ Knowledge base saved to: {output_file}")

# ============================================================================
# PART 4: Process Multiple Notes (Batch)
# ============================================================================

print("\n\n" + "="*80)
print("PART 4: BATCH PROCESSING MULTIPLE NOTES")
print("="*80)

clinical_notes = [
    "Patient with DM2 and HTN presents with chest pain. Started on aspirin and nitroglycerin.",
    "History of COPD exacerbation, admitted for respiratory distress. On albuterol and prednisone.",
    "Acute kidney injury secondary to dehydration. Cr elevated to 2.5. Starting IV fluids.",
    "New diagnosis of atrial fibrillation. Anticoagulation with warfarin initiated.",
    "Post-op day 1 s/p CABG. Stable hemodynamics. Continue statin and beta blocker.",
]

print(f"\nProcessing {len(clinical_notes)} clinical notes...")
print("-"*80)

batch_results = []

for note_num, note in enumerate(clinical_notes, 1):
    doc = nlp(note)

    # Extract key info
    diseases = [ent.text for ent in doc.ents if ent.label_ == "DISEASE"]
    meds = [ent.text for ent in doc.ents if ent.label_ == "CHEMICAL"]
    abbrs = len(doc._.abbreviations) if doc._.abbreviations else 0
    linked = sum(1 for ent in doc.ents if ent._.kb_ents)

    result = {
        'note_id': f'N{note_num:03d}',
        'text': note,
        'entities_total': len(doc.ents),
        'diseases': diseases,
        'medications': meds,
        'abbreviations': abbrs,
        'linked_entities': linked,
    }

    batch_results.append(result)

    print(f"\nNote {note_num}:")
    print(f"  Text: {note[:60]}...")
    print(f"  Entities: {len(doc.ents)} | Diseases: {len(diseases)} | Meds: {len(meds)} | Linked: {linked}")

# Aggregate statistics
print("\n\n📈 BATCH STATISTICS:")
print("-"*80)

total_entities = sum(r['entities_total'] for r in batch_results)
total_diseases = sum(len(r['diseases']) for r in batch_results)
total_meds = sum(len(r['medications']) for r in batch_results)
total_linked = sum(r['linked_entities'] for r in batch_results)

print(f"Total notes processed: {len(clinical_notes)}")
print(f"Total entities extracted: {total_entities}")
print(f"Total diseases found: {total_diseases}")
print(f"Total medications found: {total_meds}")
print(f"Total UMLS links: {total_linked}")
print(f"Average entities per note: {total_entities/len(clinical_notes):.1f}")
print(f"Link success rate: {total_linked/total_entities*100:.1f}%")

# Save batch results
batch_output = "batch_extraction_results.json"
with open(batch_output, 'w') as f:
    json.dump(batch_results, f, indent=2)

print(f"\n✓ Batch results saved to: {batch_output}")

# ============================================================================
# PART 5: Clinical Insights Dashboard
# ============================================================================

print("\n\n" + "="*80)
print("PART 5: CLINICAL INSIGHTS DASHBOARD")
print("="*80)

# Collect all diseases from batch
all_diseases = []
for result in batch_results:
    all_diseases.extend(result['diseases'])

# Collect all medications
all_medications = []
for result in batch_results:
    all_medications.extend(result['medications'])

# Count frequencies
disease_freq = Counter(all_diseases)
med_freq = Counter(all_medications)

print("\n🔝 TOP 5 MOST COMMON DISEASES:")
print("-"*80)
for disease, count in disease_freq.most_common(5):
    print(f"  {disease:<40} ({count} occurrences)")

print("\n\n💊 TOP 5 MOST COMMON MEDICATIONS:")
print("-"*80)
for med, count in med_freq.most_common(5):
    print(f"  {med:<40} ({count} occurrences)")

# Disease-Medication Pairs
print("\n\n🔗 DISEASE-MEDICATION ASSOCIATIONS:")
print("-"*80)

associations = []
for result in batch_results:
    if result['diseases'] and result['medications']:
        for disease in result['diseases']:
            for med in result['medications']:
                associations.append((disease, med))

if associations:
    assoc_freq = Counter(associations)
    print("\nTop associations found in notes:")
    for (disease, med), count in assoc_freq.most_common(5):
        print(f"  {disease} → {med} ({count}x)")
else:
    print("  No disease-medication associations found in this batch")

# ============================================================================
# PART 6: Pipeline Summary
# ============================================================================

print("\n\n" + "="*80)
print("PIPELINE SUMMARY & CAPABILITIES")
print("="*80)

summary = f"""
✅ PIPELINE COMPONENTS:
   1. Biomedical Named Entity Recognition (NER)
   2. Abbreviation Detection & Resolution
   3. UMLS Entity Linking & Normalization

📊 PROCESSING STATISTICS:
   - Single note: {len(doc.ents)} entities extracted
   - Batch processing: {len(clinical_notes)} notes in {len(batch_results)} results
   - Total unique diseases: {len(set(all_diseases))}
   - Total unique medications: {len(set(all_medications))}
   - UMLS linking success: {total_linked/total_entities*100:.1f}%

💾 OUTPUT FILES GENERATED:
   - patient_knowledge_base.json (single note structured data)
   - batch_extraction_results.json (batch processing results)

🎯 CAPABILITIES DEMONSTRATED:
   ✓ Extract medical entities from clinical text
   ✓ Detect and resolve medical abbreviations
   ✓ Link entities to standardized UMLS concepts
   ✓ Build structured knowledge bases
   ✓ Process single notes or batches
   ✓ Generate clinical insights and statistics
   ✓ Identify disease-medication associations

🚀 PRODUCTION READY:
   This pipeline can be integrated into:
   - EHR systems for automated coding
   - Clinical decision support systems
   - Medical research data extraction
   - Population health analytics
   - Drug safety surveillance
"""

print(summary)

print("\n" + "="*80)
print("DAY 10 COMPLETE! 🎉")
print("="*80)

completion_message = 

print(completion_message)