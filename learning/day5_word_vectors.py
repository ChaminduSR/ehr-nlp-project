import spacy

nlp = spacy.load("en_core_web_md")

print("=" * 80)
print("WORD VECTORS AND SEMANTIC SIMILARITY")
print("=" * 80)

medical_words = [
    "fever",
    "cough",
    "medication",
    "diabetes",
    "infection",
    "pain",
]

print("\n\nPart 1: Word Vectors")
print("-" * 80)

for word in medical_words:
    doc = nlp(word)
    token = doc[0]
    vector = token.vector

    print(f"\nWord: {word}")
    print(f"Vector length: {len(vector)}")
    print(f"First 10 dimensions: {vector[:10]}")
    print(f"Vector magnitude (length): {token.vector_norm:.4f}")

print("\n\n" + "=" * 80)
print("Part 2: Similarity Between Word Pairs")
print("=" * 80)

word_pairs = [
    ("fever", "cough"),
    ("fever", "temperature"),
    ("medication", "drug"),
    ("fever", "medication"),
    ("diabetes", "infection"),
    ("pain", "cough"),
    ("patient", "doctor"),
]

print(f"\n{'Word 1':<15} {'Word 2':<15} {'Similarity':<15} {'Meaning'}")
print("-" * 80)

for word1, word2 in word_pairs:
    doc1 = nlp(word1)
    doc2 = nlp(word2)

    similarity = doc1.similarity(doc2)

    if similarity > 0.7:
        meaning = "Very similar (same concept)"
    elif similarity > 0.5:
        meaning = "Similar (related concepts)"
    elif similarity > 0.3:
        meaning = "Somewhat similar"
    else:
        meaning = "Different concepts"

    print(f"{word1:<15} {word2:<15} {similarity:<15.4f} {meaning}")

print("\n\n" + "=" * 80)
print("Part 3: Finding Most Similar Words")
print("=" * 80)

target_word = "fever"
doc_target = nlp(target_word)

print(f"\nFinding words most similar to: '{target_word}'")
print("-" * 80)

test_words = [
    "cough",
    "temperature",
    "illness",
    "medication",
    "pain",
    "headache",
    "chills",
    "malaise",
    "symptom",
]

similarities = []
for test_word in test_words:
    doc_test = nlp(test_word)
    sim = doc_target.similarity(doc_test)
    similarities.append((test_word, sim))

similarities.sort(key=lambda x: x[1], reverse=True)

print(f"\n{'Rank':<6} {'Word':<15} {'Similarity':<15}")
print("-" * 80)

for rank, (word, sim) in enumerate(similarities, 1):
    print(f"{rank:<6} {word:<15} {sim:<15.4f}")

print("\n\n" + "=" * 80)
print("Part 4: Sentence Similarity")
print("=" * 80)

sentences = [
    "Patient has fever",
    "Patient has elevated temperature",
    "Patient is prescribed antibiotics",
    "Doctor gave medication",
]

print("\nSentence Similarity Matrix:")
print("-" * 80)

docs = [nlp(sent) for sent in sentences]

print(f"\n{'Sentence 1':<35} {'Sentence 2':<35} {'Similarity':<15}")
print("-" * 80)

for i, doc1 in enumerate(docs):
    for j, doc2 in enumerate(docs):
        if i < j:
            similarity = doc1.similarity(doc2)
            print(f"{sentences[i]:<35} {sentences[j]:<35} {similarity:<15.4f}")

print("\n" + "=" * 80)
print("KEY CONCEPTS:")
print("=" * 80)
print("""
1. WORD VECTORS: Numbers that represent word meaning
   - Each word has a 96-dimensional vector
   - Similar words have similar vectors

2. SIMILARITY SCORE: How similar two words/sentences are
   - Range: 0.0 (completely different) to 1.0 (identical)
   - > 0.7 = Very similar
   - 0.5-0.7 = Similar
   - < 0.3 = Different

3. USE CASES FOR EHR:
   - Find alternative ways to express symptoms
   - Normalize medical terminology
   - Find related clinical concepts
   - Group similar patient presentations
""")
