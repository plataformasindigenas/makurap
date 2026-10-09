#!/usr/bin/env python3
"""Build data/fauna.yaml and data/ethnobotany.yaml for Makurap.

The BILingo deck ships no images, so we reuse the Bororo (boeenomoto) and
Enawene-Nawe (enawenenawe) photo collections: any species that already has a
photo in a sibling platform is matched by scientific name and cached, by stable
name, into makurap/media/images/ (committed). The cache is the source of truth
at deploy time, so the build does NOT depend on the sibling repos being present
(e.g. on Cloudflare Pages, where only this repo is checked out). When the
siblings ARE present the cache is refreshed from them.

We also write the matched scientific names back into data/dictionary.tsv so
that terradoc's dictionary <-> fauna/ethnobotany cross-linking lights up.

Makurap names and Portuguese glosses come from the BILingo word list; the
scientific identifications are the standard ones for the common Amazonian
species named, and are intentionally conservative (genus-level where the gloss
is generic). Everything here is DRAFT pending community/specialist review.
"""
import shutil
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIBLINGS = [ROOT.parent / "boeenomoto", ROOT.parent / "enawenenawe"]
# Committed cache of reused photos (source of truth at deploy time).
IMG_CACHE = ROOT / "media" / "images"
IMG_CACHE.mkdir(parents=True, exist_ok=True)

# scientific_name (lower) -> (abs source image path)
photo_index: dict[str, Path] = {}
for site in SIBLINGS:
    for mod in ("fauna", "ethnobotany"):
        fy = site / "data" / f"{mod}.yaml"
        if not fy.exists():
            continue
        for e in yaml.safe_load(fy.read_text(encoding="utf-8")) or []:
            sn = (e.get("scientific_name") or "").strip().lower()
            pic = e.get("pic_link")
            if sn and pic:
                src = site / "docs" / pic
                if src.exists():
                    photo_index.setdefault(sn, src)

# Each tuple: Makurap, Portuguese, scientific_name, image_key (sci to reuse,
# or None), classification/info note.
FAUNA = [
    ("amenko", "onça", "Panthera onca", "panthera onca", "Maior felino das Américas; nome de um dos clãs Makurap."),
    ("takri", "onça-feroz", "Panthera onca", "panthera onca", "Designação para a onça em sua forma mais perigosa."),
    ("uax", "anta", "Tapirus terrestris", "tapirus terrestris", "Maior mamífero terrestre da região; caça apreciada."),
    ("uro", "tatu", "Dasypus novemcinctus", "dasypus novemcinctus", "Tatu-galinha, caça comum."),
    ("wiriyo", "tatu-canastra", "Priodontes maximus", "priodontes maximus", "O maior dos tatus."),
    ("atax", "paca", "Cuniculus paca", "cuniculus paca", "Roedor noturno muito apreciado na caça."),
    ("utu", "veado", "Mazama americana", "mazama americana", "Veado-mateiro."),
    ("arembo", "macaco-preto", "Sapajus apella", "simia apella", "Macaco-prego."),
    ("karoroy", "macaco-velho", "Sapajus apella", "simia apella", "Termo para o macaco-prego adulto."),
    ("mitõ", "mutum", "Mitu tuberosum", "mitu tuberosum", "Ave de caça; nome de clã (Mitum)."),
    ("payo", "pato", "Cairina moschata", "cairina moschata", "Pato-do-mato."),
    ("paliõn", "gavião", "Rupornis magnirostris", "rupornis magnirostris", "Gavião comum."),
    ("pãriõ xato", "gavião-real", "Harpia harpyja", "harpia harpyja", "A maior águia das Américas."),
    ("wato", "jacaré", "Caiman yacare", "caiman yacare", "Jacaré-do-pantanal/regional."),
    ("xat", "jararaca / cobra", "Viperidae", "família: viperidae", "Serpente peçonhenta; nome de clã (Xát)."),
    ("andole", "peixe pintado", "Pseudoplatystoma sp.", "zungaro zungaro", "Grande bagre de couro pintado."),
    ("njalule", "borboleta", "Lepidoptera", "ordem: lepidoptera", "Borboleta."),
]

ETHNO = [
    ("arao", "castanha-do-Brasil", "Bertholletia excelsa", None, "Castanha-do-Pará — coleta de grande importância econômica.", "alimento, comércio"),
    ("wirixa", "açaí", "Euterpe oleracea", "euterpe oleracea", "Palmeira cujo fruto é coletado pelos homens.", "alimento"),
    ("iko", "urucum", "Bixa orellana", "bixa orellana", "Fonte do pigmento vermelho; nomeia o clã Ikô.", "tinta corporal, ritual"),
    ("arawu", "amendoim", "Arachis hypogaea", "arachis hypogaea", "Cultivado nas roças.", "alimento"),
    ("orokone", "tucumã", "Astrocaryum aculeatum", None, "Palmeira cuja fibra é usada para tecer o marico.", "fibra, alimento"),
    ("mbeku", "cana-de-açúcar", "Saccharum officinarum", None, "Cultivada nas roças.", "alimento"),
    ("ndutnda", "cacau", "Theobroma cacao", None, "Cacau nativo.", "alimento"),
]


def copy_image(sci_key: str, slug: str) -> str | None:
    """Ensure media/images/<slug>.jpg exists; return its pic_link, or None.

    Refreshes from a sibling photo when available; otherwise relies on the
    already-committed cache (so deploy builds without the siblings still work).
    """
    dest_name = f"{slug}.jpg"
    dest = IMG_CACHE / dest_name
    src = photo_index.get((sci_key or "").lower())
    if src:
        shutil.copy2(src, dest)
    if dest.exists():
        return f"images/{dest_name}"
    return None


# --- Build fauna ----------------------------------------------------------
fauna = []
sci_for_dict: dict[str, str] = {}
for i, (mk, pt, sci, key, info) in enumerate(FAUNA, 1):
    pic = copy_image(key, f"makurap_fauna_{i:02d}") if key else None
    rec = {"id": i, "name_indigenous": mk, "name_portuguese": pt,
           "scientific_name": sci, "info": info}
    if pic:
        rec["pic_link"] = pic
    fauna.append(rec)
    sci_for_dict[mk.lower()] = sci

(ROOT / "data" / "fauna.yaml").write_text(
    yaml.safe_dump(fauna, allow_unicode=True, sort_keys=False), encoding="utf-8")

# --- Build ethnobotany ----------------------------------------------------
ethno = []
for i, (mk, pt, sci, key, desc, usage) in enumerate(ETHNO, 1):
    pic = copy_image(key, f"makurap_flora_{i:02d}") if key else None
    rec = {"id": i, "name_indigenous": mk, "name_portuguese": pt,
           "scientific_name": sci, "usage": usage, "descriptions_of_use": desc}
    if pic:
        rec["pic_link"] = pic
    ethno.append(rec)
    sci_for_dict[mk.lower()] = sci

(ROOT / "data" / "ethnobotany.yaml").write_text(
    yaml.safe_dump(ethno, allow_unicode=True, sort_keys=False), encoding="utf-8")

# --- Patch dictionary.tsv with scientific names (col index 6) -------------
dict_path = ROOT / "data" / "dictionary.tsv"
lines = dict_path.read_text(encoding="utf-8").splitlines()
header = lines[0].split("\t")
si = header.index("scientific_name")
ei = header.index("entry")
patched = 0
out = [lines[0]]
for line in lines[1:]:
    cols = line.split("\t")
    sci = sci_for_dict.get(cols[ei].strip().lower())
    if sci and not cols[si]:
        cols[si] = sci
        patched += 1
    out.append("\t".join(cols))
dict_path.write_text("\n".join(out) + "\n", encoding="utf-8")

n_fauna_img = sum(1 for f in fauna if f.get("pic_link"))
n_flora_img = sum(1 for f in ethno if f.get("pic_link"))
print(f"Fauna: {len(fauna)} entries ({n_fauna_img} with reused photos)")
print(f"Ethnobotany: {len(ethno)} entries ({n_flora_img} with reused photos)")
print(f"Patched {patched} dictionary rows with scientific names")
