# RAGAS Evaluation Dataset — Gale Encyclopedia of Medicine (2nd Ed.)

## Overview
This dataset contains **51 evaluation samples** for assessing a RAG-based medical chatbot 
grounded in the *Gale Encyclopedia of Medicine, 2nd Edition*.

Each sample follows the RAGAS evaluation format with four fields:
- **question** — The user query
- **answer** — The expected chatbot answer
- **contexts** — Source passage(s) from the book (used to evaluate faithfulness & context recall)
- **ground_truth** — The concise gold-standard answer

---

## Files
| File | Description |
|------|-------------|
| `ragas_medical_evaluation_dataset.json` | Primary format — list of dicts with `contexts` as arrays |
| `ragas_medical_evaluation_dataset.csv`  | Spreadsheet-friendly, `contexts` joined with ` \|\|\| ` |

---

## Question Types (16 categories)
| Type | Count | RAGAS Metric Focus |
|------|-------|--------------------|
| factual | 6 | Answer Correctness, Faithfulness |
| pharmacology | 6 | Faithfulness, Context Precision |
| definition | 5 | Answer Correctness |
| mechanism | 5 | Faithfulness, Answer Relevance |
| treatment | 4 | Faithfulness, Context Recall |
| procedural | 4 | Answer Relevance, Faithfulness |
| comparison | 3 | Answer Correctness, Context Recall |
| diagnostic | 3 | Faithfulness, Context Precision |
| multi_hop | 3 | Context Recall (multi-doc) |
| epidemiology | 3 | Answer Correctness |
| yes_no | 2 | Answer Correctness |
| prognosis | 2 | Faithfulness |
| prevention | 2 | Answer Relevance |
| clinical_judgment | 1 | Faithfulness |
| complication | 1 | Answer Correctness |
| clinical_impact | 1 | Faithfulness |

---

## Topics Covered
| Topic | Samples |
|-------|---------|
| Achalasia | 13 |
| General Anesthesia | 10 |
| Abuse | 8 |
| Acetaminophen | 6 |
| Aplastic Anemia | 5 |
| Abscess | 4 |
| Aphasia | 3 |
| Achondroplasia | 2 |

---

## Usage with RAGAS

```python
from datasets import Dataset
import json

# Load dataset
with open("ragas_medical_evaluation_dataset.json") as f:
    data = json.load(f)

dataset = Dataset.from_list(data)

# Run RAGAS evaluation
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
    answer_correctness,
)

result = evaluate(
    dataset=dataset,
    metrics=[
        faithfulness,
        answer_relevancy,
        context_recall,
        context_precision,
        answer_correctness,
    ],
)

print(result)
df = result.to_pandas()
```

## Key RAGAS Metrics Explained
- **Faithfulness** — Is the answer grounded in the provided context?
- **Answer Relevancy** — Does the answer address the question?
- **Context Recall** — Does the retrieved context contain the ground truth?
- **Context Precision** — Is the retrieved context focused / not noisy?
- **Answer Correctness** — How close is the answer to the ground truth?
