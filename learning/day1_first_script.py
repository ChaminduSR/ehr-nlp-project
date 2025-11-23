import spacy

nlp = spacy.load("en_core_web_sm")

clinical_note = "Patient reports fever and cough. No chest pain. History of diabetes."

doc = nlp(clinical_note)

print("Original text:")
print(clinical_note)
print("\n" + "="*50)

print("\nTokens (individual words):")
for token in doc:
    print(f"  {token.text}")

print("\n" + "="*50)
print("\nTokens with details:")
for token in doc:
    print(f"  {token.text:15} | POS: {token.pos_:8} | Lemma: {token.lemma_}")
