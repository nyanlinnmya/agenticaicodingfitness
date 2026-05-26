---
name: rag-knowledge-agents
description: "Teach Retrieval-Augmented Generation (RAG) — how to ground an LLM in your own documents so it answers from facts instead of guessing. Covers embeddings, vector search, chunking, the retrieve-then-generate loop, and when RAG beats stuffing everything in the prompt. Use when someone asks 'how do I make the AI answer from my docs/PDFs?', mentions embeddings/vector DBs/hallucination, or is reviewing Week 8."
when_to_use: "Learner wants the model to answer from their own documents/knowledge base, asks about embeddings/vector search/RAG/hallucination, or is catching up on Week 8."
---

# RAG & Knowledge Agents — Grounding the Model in Your Facts (Week 8)

> **The one idea:** LLMs make things up when they don't know. **RAG** fixes this by *retrieving* the most relevant chunks of *your* documents and pasting them into the prompt before the model answers. The model stops guessing and starts quoting your sources.

```
Question → find the most relevant doc chunks → put them in the prompt → model answers from them
```

---

## Why not just paste the whole document?

- **Context limits & cost** — you can't fit a 500-page manual in every prompt, and you'd pay for all of it every time.
- **Noise** — burying the answer in 500 pages makes the model *worse*, not better.
- RAG sends only the handful of chunks that actually matter for *this* question.

---

## The four moving parts

### 1. Chunking
Split documents into bite-sized pieces (a few paragraphs each). You retrieve *chunks*, not whole files, so the model gets just the relevant slice.

### 2. Embeddings — turning meaning into numbers
An **embedding** is a vector (a list of numbers) that captures the *meaning* of a chunk. Texts about the same topic land near each other in vector space, even with different wording. "How do I reset my password?" sits near "account recovery steps" — no shared keywords needed.

```python
# Conceptual — embed each chunk once, store the vectors
chunks = split_into_chunks(documents)         # ["...", "...", ...]
vectors = embed(chunks)                        # each chunk → [0.12, -0.4, ...]
store(vectors, chunks)                         # in a vector DB (Chroma, FAISS, pgvector, ...)
```

### 3. Vector search (semantic search)
At question time, embed the *question* and find the chunks whose vectors are closest (cosine similarity). Those are your most-relevant passages.

```python
q_vector = embed([question])[0]
top_chunks = store.search(q_vector, k=4)       # 4 nearest chunks
```

### 4. Augmented generation
Paste the retrieved chunks into the prompt and ask the model to answer *using only those*.

```python
context = "\n\n".join(top_chunks)
prompt = f"""Answer using ONLY the context below. If it's not there, say you don't know.

Context:
{context}

Question: {question}"""

answer = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{"role": "user", "content": prompt}],
).content[0].text
```

That instruction — *"use ONLY the context, say 'I don't know' otherwise"* — is what kills hallucination. The model is now a librarian reading from your shelf, not a know-it-all.

> 📁 Class repo: `week8/Week8_RAG_Knowledge_Agents_Lab.pdf` — the full lab walkthrough.

---

## The whole RAG flow

```
INDEX (once):   docs → chunk → embed → store in vector DB
                                          │
QUERY (each Q): question → embed → search ┘→ top-k chunks → prompt → grounded answer
```

---

## RAG vs. the other "memory" you'll meet

- **RAG (Week 8)** = retrieve relevant *text/documents* by meaning. Great for manuals, wikis, PDFs, support docs.
- **Knowledge-graph memory (Week 14)** = store *structured facts and relationships* (this room → has → this sensor) and query them with Cypher. Great for connected, evolving state.
- **GraphRAG** combines them: retrieve over a graph instead of a flat pile of text. (See the `agent-memory-graphs` skill.)

Different tools for different shapes of knowledge — knowing which to reach for is the skill.

---

## When to use RAG (and when not to)
✅ Answers must come from *your* private/large/changing documents.
✅ You need citations / "where did this come from?"
✅ The corpus is too big for the context window.
❌ The question is general knowledge the model already has.
❌ Everything relevant easily fits in the prompt — then just paste it (simpler, no infra).

---

## 🧪 Guided lab (offer this)

Build a tiny "chat with your docs" from scratch:

1. **Pick a source.** A README, a PDF, or a few markdown files they care about.
2. **Chunk it.** Split into ~500-word pieces. Have them eyeball the chunks so "chunk" stops being abstract.
3. **Embed + store.** Use any embedding model + a simple store (even a Python list with cosine similarity is fine for learning — no DB needed at first). Embed each chunk.
4. **Retrieve.** Embed a question, compute similarity to every chunk, print the top 3. Have them confirm the right passages surfaced.
5. **Generate.** Feed those 3 chunks + the "use ONLY this context" prompt to the model. Ask a question whose answer is in the docs, and one whose answer *isn't* — show it correctly says "I don't know" for the second.
6. **Break it to learn it.** Retrieve only 1 chunk, or skip the "use only context" instruction, and watch quality/hallucination change. Restore.
7. **Stretch:** swap the Python-list store for a real vector DB (Chroma/FAISS), and discuss chunk size trade-offs (too big = noise, too small = lost context).

End by contrasting it with Week 14: "RAG retrieves *text*; next we'll give agents *structured* memory in a knowledge graph."
