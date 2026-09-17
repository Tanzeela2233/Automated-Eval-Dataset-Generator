import io
import json
import pandas as pd


def build_jsonl(dataset):
    buffer = io.StringIO()
    for row in dataset:
        buffer.write(json.dumps(row, ensure_ascii=False) + "\n")
    return buffer.getvalue().encode("utf-8")


def build_csv(dataset):
    records = []
    for row in dataset:
        records.append(
            {
                "input": row["input"],
                "expected_output": row["expected_output"],
                "score": row["evaluation"]["score"],
                "passed": row["evaluation"]["passed"],
                "reason": row["evaluation"]["reason"],
            }
        )

    df = pd.DataFrame(records)
    return df.to_csv(index=False).encode("utf-8")
