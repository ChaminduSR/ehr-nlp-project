import spacy
from scispacy.abbreviation import AbbreviationDetector

print("="*80)
print("DAY 8: ABBREVIATION DETECTION & RESOLUTION")
print("="*80)

print("\nLoading biomedical model...")
nlp = spacy.load("en_core_sci_sm")

print("Adding abbreviation detector to pipeline...")
nlp.add_pipe("abbreviation_detector")
print("✓ Setup complete!")

print("\n\nPart 1: Basic Abbreviation Detection")
print("-"*80)

sample_text = """
Patient with HTN and DM2 presents to ER with SOB.
Medical history: CAD s/p CABG, COPD, CKD stage 3.
Current medications include ACEI, metformin, and ASA.
"""

print(f"Text: {sample_text}\n")

doc = nlp(sample_text)

print("Detected Abbreviations:")
print(f"{'Abbreviation':<20} {'Long Form':<40} {'Definition Start':<15}")
print("-"*80)

if doc._.abbreviations:
    for abbr in doc._.abbreviations:
        print(f"{str(abbr):<20} {str(abbr._.long_form):<40} {abbr._.long_form.start:<15}")
else:
    print("No abbreviations detected")

print("\n\nPart 2: Detailed Abbreviation Information")
print("-"*80)

clinical_note = """
The patient has a history of congestive heart failure (CHF) and 
chronic obstructive pulmonary disease (COPD). Recent labs show 
elevated brain natriuretic peptide (BNP) and decreased estimated 
glomerular filtration rate (eGFR). The electrocardiogram (ECG) 
demonstrates atrial fibrillation (AFib).
"""

print(f"Clinical Note: {clinical_note}\n")

doc = nlp(clinical_note)

print("Abbreviation Details:")
print("-"*80)

for abbr in doc._.abbreviations:
    print(f"\nAbbreviation: {abbr}")
    print(f"  Long form: {abbr._.long_form}")
    print(f"  Abbr position: characters {abbr.start_char} to {abbr.end_char}")
    print(f"  Long form position: characters {abbr._.long_form.start_char} to {abbr._.long_form.end_char}")
    print(f"  Sentence: {abbr.sent.text.strip()}")

print("\n\nPart 3: Extract Abbreviation Pairs")
print("-"*80)

text_with_abbrs = """
Patient diagnosed with acute myocardial infarction (AMI) and transferred to 
cardiac intensive care unit (CICU). Started on tissue plasminogen activator (tPA).
Follow-up with percutaneous coronary intervention (PCI) scheduled.
"""

print(f"Text: {text_with_abbrs}\n")

doc = nlp(text_with_abbrs)

# Create abbreviation dictionary
abbr_dict = {}
for abbr in doc._.abbreviations:
    abbr_dict[str(abbr)] = str(abbr._.long_form)

print("Abbreviation Dictionary:")
for short, long in abbr_dict.items():
    print(f"  {short:<10} → {long}")

print("\n\nPart 4: Common Clinical Abbreviations")
print("-"*80)

common_abbrs_text = """
PMH: HTN, DM2, CAD s/p CABG
Medications: ASA, ACEI, BB, statin
ROS: denies CP, SOB, N/V
PE: VS stable, HEENT normal, CV RRR, Lungs CTAB
Labs: BMP, CBC, LFTs WNL
Imaging: CXR shows cardiomegaly, no acute process on CT head
"""

print(f"Clinical Note: {common_abbrs_text}\n")

doc = nlp(common_abbrs_text)

if doc._.abbreviations:
    print("Detected abbreviations:")
    for abbr in doc._.abbreviations:
        print(f"  - {abbr} → {abbr._.long_form}")
else:
    print("Note: This text contains many abbreviations, but they may not")
    print("be detected without their long forms present in the text.")
    print("The abbreviation detector works best when both forms appear together.")

print("\n\nPart 5: Build Custom Abbreviation Database")
print("-"*80)

# Multiple notes with abbreviations
notes_with_definitions = [
    "Patient has hypertension (HTN) and diabetes mellitus type 2 (DM2).",
    "Started on angiotensin-converting enzyme inhibitor (ACEI) for blood pressure.",
    "Electrocardiogram (ECG) shows normal sinus rhythm.",
    "Chest X-ray (CXR) demonstrates no acute findings.",
    "Blood urea nitrogen (BUN) and creatinine within normal limits.",
]

print("Processing multiple notes to build abbreviation database:\n")

# Aggregate all abbreviations
abbreviation_database = {}

for note_num, note in enumerate(notes_with_definitions, 1):
    doc = nlp(note)
    print(f"Note {note_num}: {note}")
    
    if doc._.abbreviations:
        print("  Found:")
        for abbr in doc._.abbreviations:
            abbr_short = str(abbr)
            abbr_long = str(abbr._.long_form)
            abbreviation_database[abbr_short] = abbr_long
            print(f"    {abbr_short} → {abbr_long}")
    else:
        print("  No abbreviations detected")
    print()

print("-"*80)
print(f"\nAbbreviation Database ({len(abbreviation_database)} entries):")
for short, long in sorted(abbreviation_database.items()):
    print(f"  {short:<10} = {long}")

print("\n\nPart 6: Resolve Abbreviations in New Text")
print("-"*80)

# New text with abbreviations (no definitions)
new_note = """
67 y/o M with PMH of HTN, DM2, CAD presents with CP and SOB.
VS: BP 160/95, HR 110, RR 24, O2 sat 88% on RA.
ECG shows ST elevation. CXR reveals pulmonary edema.
Labs: elevated BUN and troponin.
Dx: acute MI with CHF exacerbation.
"""

print(f"New Clinical Note: {new_note}\n")

doc = nlp(new_note)

print("Abbreviations in this note:")
if doc._.abbreviations:
    for abbr in doc._.abbreviations:
        print(f"  {abbr} → {abbr._.long_form}")
else:
    print("  No abbreviations auto-detected (definitions not in text)")

print("\nUsing our abbreviation database to resolve:")
# Manual resolution using our database
text_words = new_note.split()
resolved_abbrs = []
for word in text_words:
    clean_word = word.strip('.,;:')
    if clean_word in abbreviation_database:
        resolved_abbrs.append(f"{clean_word} ({abbreviation_database[clean_word]})")
    
if resolved_abbrs:
    for resolved in resolved_abbrs:
        print(f"  {resolved}")
else:
    print("  (Some abbreviations may not be in our database)")

print("\n\nPart 7: Statistics and Analysis")
print("-"*80)

all_notes = notes_with_definitions + [new_note]
total_abbrs = 0
total_notes = len(all_notes)

for note in all_notes:
    doc = nlp(note)
    total_abbrs += len(doc._.abbreviations)

print(f"Total notes processed: {total_notes}")
print(f"Total abbreviations detected: {total_abbrs}")
print(f"Average abbreviations per note: {total_abbrs/total_notes:.2f}")
print(f"Unique abbreviations in database: {len(abbreviation_database)}")

print("\n" + "="*80)
print("HOW ABBREVIATION DETECTION WORKS")
print("="*80)

explanation = """
The scispaCy AbbreviationDetector uses the Schwartz-Hearst algorithm:

1. PATTERN MATCHING
   - Looks for patterns like: "long form (ABBR)"
   - Example: "congestive heart failure (CHF)"

2. CHARACTER MATCHING
   - Checks if abbreviation letters match long form
   - CHF matches: Congestive Heart Failure
   - First letters or important letters

3. CONTEXT WINDOW
   - Searches nearby text for potential long forms
   - Uses linguistic rules to validate matches

4. LIMITATIONS
   - Needs both abbreviation and long form in same document
   - May miss abbreviations without explicit definitions
   - Works best with standard medical abbreviation patterns

5. BEST PRACTICES
   - Build abbreviation database from training data
   - Combine with manual abbreviation dictionaries
   - Validate detections for your specific use case
"""

print(explanation)

print("\n" + "="*80)
print("COMMON CLINICAL ABBREVIATIONS REFERENCE")
print("="*80)

common_abbrs = {
    "HTN": "Hypertension",
    "DM": "Diabetes Mellitus",
    "DM2": "Diabetes Mellitus Type 2",
    "CAD": "Coronary Artery Disease",
    "MI": "Myocardial Infarction",
    "CHF": "Congestive Heart Failure",
    "COPD": "Chronic Obstructive Pulmonary Disease",
    "CKD": "Chronic Kidney Disease",
    "SOB": "Shortness of Breath",
    "CP": "Chest Pain",
    "CABG": "Coronary Artery Bypass Graft",
    "PCI": "Percutaneous Coronary Intervention",
    "ACEI": "Angiotensin-Converting Enzyme Inhibitor",
    "ASA": "Aspirin",
    "BB": "Beta Blocker",
    "ECG/EKG": "Electrocardiogram",
    "CXR": "Chest X-Ray",
    "BMP": "Basic Metabolic Panel",
    "CBC": "Complete Blood Count",
    "BUN": "Blood Urea Nitrogen",
    "BNP": "Brain Natriuretic Peptide",
    "eGFR": "Estimated Glomerular Filtration Rate",
}

print("\nFrequently Used Clinical Abbreviations:\n")
for abbr, full in sorted(common_abbrs.items()):
    print(f"  {abbr:<12} = {full}")
