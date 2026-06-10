# RAG Chatbot Test Questions

This document contains test questions used to evaluate the FIFA 26 Football RAG Chatbot.

The purpose of these tests is to check:

* Answer accuracy
* Retrieval quality
* Source grounding
* Hallucination control
* Missing-information handling
* User-facing response quality

---

## 1. Answerable Questions

These questions should be answerable from the local football knowledge base.

### Q1. Which countries are hosting the 2026 FIFA World Cup?

Expected answer should mention:

* United States
* Canada
* Mexico

Expected source:

* 2026 FIFA World Cup

---

### Q2. Who won the 2022 FIFA World Cup?

Expected answer should mention:

* Argentina won the 2022 FIFA World Cup.
* Argentina defeated France on penalties after the match ended 3–3 after extra time.

Expected source:

* 2022 FIFA World Cup

---

### Q3. What is association football?

Expected answer should explain:

* Association football is a team sport.
* It is played between two teams.
* It is commonly known as football or soccer in some countries.

Expected source:

* Association football

---

### Q4. How often is the FIFA World Cup held?

Expected answer should mention:

* The FIFA World Cup is usually held every four years.

Expected source:

* FIFA World Cup

---

### Q5. What is the FIFA World Cup?

Expected answer should explain:

* It is an international association football competition.
* It is contested by senior men’s national teams.
* It is organized by FIFA.

Expected source:

* FIFA World Cup

---

## 2. Retrieval Quality Questions

These tests check whether the retriever selects the most relevant source documents.

### Q1. Which countries are hosting the 2026 FIFA World Cup?

Expected primary source:

* 2026 FIFA World Cup

Reason:

The answer is directly related to the tournament hosts and should retrieve chunks from the 2026 FIFA World Cup article.

---

### Q2. Who won the 2022 FIFA World Cup?

Expected primary source:

* 2022 FIFA World Cup

Reason:

The answer is directly related to the final result of the 2022 tournament.

---

### Q3. What are some FIFA World Cup records?

Expected primary source:

* FIFA World Cup records and statistics

Reason:

The question asks about records, so the system should retrieve chunks related to records and statistics.

---

### Q4. What is the history of the FIFA World Cup?

Expected primary source:

* History of the FIFA World Cup

Reason:

The question asks for historical information and should retrieve the history-related article.

---

## 3. Hallucination Control Questions

These questions should not be answered with guesses or predictions.

The chatbot should only answer from retrieved source context.

If the information is missing, the expected response is:

`The requested target info is missing from the provided dataset.`

---

### Q1. Who will win the 2026 FIFA World Cup?

Expected response:

`The requested target info is missing from the provided dataset.`

Reason:

The winner of the 2026 FIFA World Cup is not known yet and should not be predicted.

---

### Q2. What will be the exact final score of the 2026 FIFA World Cup final?

Expected response:

`The requested target info is missing from the provided dataset.`

Reason:

The final has not happened yet, so the model must not invent an answer.

---

### Q3. Which player will score the most goals in the 2026 FIFA World Cup?

Expected response:

`The requested target info is missing from the provided dataset.`

Reason:

This is future information and should not be guessed.

---

### Q4. Which team will be the runner-up in the 2026 FIFA World Cup?

Expected response:

`The requested target info is missing from the provided dataset.`

Reason:

The tournament result is not available in the dataset.

---

## 4. Unrelated Questions

These questions are outside the football knowledge base.

The chatbot should not answer from general knowledge.

---

### Q1. What is the capital of Japan?

Expected response:

`The requested target info is missing from the provided dataset.`

Reason:

The knowledge base is focused on football and FIFA World Cup topics.

---

### Q2. Explain quantum computing.

Expected response:

`The requested target info is missing from the provided dataset.`

Reason:

This is outside the selected football dataset.

---

### Q3. Who is the CEO of Tesla?

Expected response:

`The requested target info is missing from the provided dataset.`

Reason:

This is unrelated to the football RAG knowledge base.

---

## 5. Edge Case Questions

These tests check input handling and response stability.

---

### Q1. Empty input

Expected behavior:

The UI should ask the user to enter a valid football or World Cup question.

---

### Q2. Very short query

Example:

`World Cup`

Expected behavior:

The chatbot should return a general answer about the FIFA World Cup if relevant context is retrieved.

---

### Q3. Misspelled query

Example:

`Who win 2022 fifa wolrd cup?`

Expected behavior:

The chatbot should still retrieve relevant information about the 2022 FIFA World Cup and answer correctly.

---

### Q4. Ambiguous query

Example:

`Tell me about records.`

Expected behavior:

The chatbot should retrieve football or FIFA World Cup records if the query matches the local knowledge base.

---

## 6. Manual Evaluation Checklist

For each tested question, check the following:

| Evaluation Point                                 | Pass/Fail |
| ------------------------------------------------ | --------- |
| Answer is relevant to the question               |           |
| Answer is based only on retrieved context        |           |
| No unsupported facts are added                   |           |
| Source summary is shown                          |           |
| Evidence preview is shown                        |           |
| Missing information returns fallback response    |           |
| UI remains readable and professional             |           |
| No technical chunk details are shown to the user |           |

---

## 7. Overall Evaluation Notes

The chatbot should be considered successful if:

* It answers football and FIFA World Cup questions correctly.
* It shows source evidence for transparency.
* It refuses to guess future or missing information.
* It avoids hallucination.
* It provides a clean and user-friendly UI.
* It keeps technical retrieval details hidden from normal users while preserving source transparency.
