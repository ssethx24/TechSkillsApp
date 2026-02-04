import re
from collections import Counter
from typing import Iterable

from .text_clean import normalize_space

def split_skills(text: str) -> list[str]:
    """
    Splits semi-structured skills like:
    'C#; .NET Core; SQL Server' or '.NET, C#, ASP.NET'
    """
    if not text:
        return []
    parts = re.split(r"[;,]\s*", str(text))
    out: list[str] = []
    for p in parts:
        p = normalize_space(p)
        if len(p) < 2:
            continue
        out.append(p)
    return out

def aggregate_skills(rows: Iterable[dict], top_n: int = 15) -> list[tuple[str, int]]:
    """
    Expects each row to have 'Skills' and 'Keywords' fields (strings).
    """
    counter = Counter()
    for row in rows:
        counter.update(split_skills(row.get("Skills", "")))
        counter.update(split_skills(row.get("Keywords", "")))
    return counter.most_common(top_n)
