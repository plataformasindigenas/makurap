#!/usr/bin/env python3
"""Build data/dictionary.tsv from the BILingo Makurap learning deck.

Source: raw/makurap_extract.json (extracted from "BILingo Makurap.xlsx").
Combines the Portuguese<->Makurap word list ("Lista", 263 pairs) with the
alphabet primer (25 letters with example words) and attaches the recorded
example phrases to any headword that appears in them.

The BILingo deck has no IPA or part-of-speech information, so POS is assigned
with a light, conservative heuristic (verbs/pronouns/numerals; everything else
left as X = unspecified) and IPA is left blank.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = json.loads((ROOT / "raw" / "makurap_extract.json").read_text(encoding="utf-8"))

# --- POS heuristics on the Portuguese gloss -------------------------------
PRONOUNS = {
    "eu", "tu", "você", "ele", "ela", "nós", "vós", "eles", "elas",
    "meu", "minha", "teu", "tua", "seu", "sua", "nosso", "nossa", "isto",
    "isso", "aquilo", "este", "esse", "aquele",
}
NUMBERS = {
    "um", "uma", "dois", "duas", "três", "quatro", "cinco", "seis", "sete",
    "oito", "nove", "dez",
}


def guess_pos(pt: str) -> str:
    g = pt.strip().lower()
    first = g.split("/")[0].split(",")[0].split("(")[0].strip()
    if first in PRONOUNS:
        return "PRON"
    if first in NUMBERS:
        return "NUM"
    # single-word Portuguese infinitive -> verb
    if re.fullmatch(r"[a-zãõáéíóúâêôç-]+(ar|er|ir)", first):
        return "V"
    return "X"


# --- Collect entries: Makurap headword -> record ---------------------------
entries: dict[str, dict] = {}


def clean(s: str) -> str:
    """Collapse internal whitespace; TSV fields must not contain tabs/newlines."""
    return re.sub(r"\s+", " ", (s or "").replace("\t", " ")).strip()


def add(mk: str, pt: str, comment: str = ""):
    # A headword cell may hold two variant spellings on separate lines.
    mk = " / ".join(p.strip() for p in re.split(r"[\r\n]+", mk or "") if p.strip())
    mk = clean(mk)
    pt = clean(pt)
    comment = clean(comment)
    if not mk or not pt:
        return
    key = mk.lower()
    if key not in entries:
        entries[key] = {"entry": mk, "definition": pt, "comment": comment,
                        "example": ""}
    else:
        e = entries[key]
        # merge a distinct gloss
        if pt.lower() not in e["definition"].lower():
            e["definition"] = f"{e['definition']}; {pt}"
        if comment and comment not in e["comment"]:
            e["comment"] = (e["comment"] + "; " + comment).strip("; ")


# Alphabet primer first (carries the letter it illustrates as a note)
for a in RAW["alphabet"]:
    note = f"Exemplo da letra «{a['letra']}» no abecedário Makurap."
    add(a["mk"], a["pt"], note)

# Main word list
for row in RAW["lista"]:
    add(row["mk"], row["pt"])

# Attach example phrases to any headword whose token appears in them
for ph in RAW["phrases"]:
    tokens = re.findall(r"[\wãõẽĩũɛə]+", ph["mk"].lower())
    for key, e in entries.items():
        hw = e["entry"].lower()
        if hw in tokens and not e["example"]:
            e["example"] = f"{ph['mk']} = {ph['pt']}"

# --- Write TSV -------------------------------------------------------------
cols = ["id", "entry", "ipa", "pos", "definition", "example_sent",
        "scientific_name", "wiki_link", "pic_link", "comment"]
rows = []
for i, e in enumerate(sorted(entries.values(), key=lambda x: x["entry"].lower()), 1):
    rows.append({
        "id": i,
        "entry": e["entry"],
        "ipa": "",
        "pos": guess_pos(e["definition"]),
        "definition": e["definition"],
        "example_sent": e["example"],
        "scientific_name": "",
        "wiki_link": "",
        "pic_link": "",
        "comment": e["comment"],
    })

out = ROOT / "data" / "dictionary.tsv"
with out.open("w", encoding="utf-8") as f:
    f.write("\t".join(cols) + "\n")
    for r in rows:
        f.write("\t".join(str(r[c]) for c in cols) + "\n")

pos_counts: dict[str, int] = {}
for r in rows:
    pos_counts[r["pos"]] = pos_counts.get(r["pos"], 0) + 1
print(f"Wrote {len(rows)} dictionary entries to {out.relative_to(ROOT)}")
print("POS distribution:", pos_counts)
print("With example sentence:", sum(1 for r in rows if r["example_sent"]))
