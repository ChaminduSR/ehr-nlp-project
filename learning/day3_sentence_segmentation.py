import spacy

nlp = spacy.load("en_core_web_sm")

clinical_note = 

doc = nlp(clinical_note)

print("Clinical Note:")
print(clinical_note)
print("\n" + "=" * 70)

print("\nSentences Found by spaCy:")
print("-" * 70)

for sent_num, sent in enumerate(doc.sents, 1):
    print(f"\nSentence {sent_num}:")
    print(f"  Text: {sent.text}")
    print(f"  Length: {len(sent)} tokens")
    print(f"  Position: Character {sent.start_char} to {sent.end_char}")

print("\n" + "=" * 70)
print("\nSentence Statistics:")
print("-" * 70)

sentence_count = len(list(doc.sents))
total_tokens = len(doc)
avg_tokens_per_sentence = (
    total_tokens / sentence_count if sentence_count > 0 else 0
)

print(f"Total sentences: {sentence_count}")
print(f"Total tokens: {total_tokens}")
print(f"Average tokens per sentence: {avg_tokens_per_sentence:.2f}")

print("\n" + "=" * 70)
print("\nTokens per Sentence:")
print("-" * 70)

for sent_num, sent in enumerate(doc.sents, 1):
    tokens = [token.text for token in sent]
    print(f"Sentence {sent_num}: {tokens}")