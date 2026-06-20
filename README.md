# Makurap — *Ki Mõyen*

Digital platform for the documentation, preservation and revitalization of the
**Makurap** language and culture (Tupí stock, **Tuparí** branch; southern
**Rondônia**, Brazil). Built with [terradoc](../terradoc), like the
[Bororo](../boeenomoto) and [Enawenê-Nawê](../enawenenawe) platforms.

> ⚠️ **Prototype / DRAFT.** Encyclopedia texts were drafted from public sources
> (ISA/Povos Indígenas no Brasil, Wikipedia, linguistic literature) and have
> **not** been reviewed by the Makurap community. Everything here is subject to
> Free, Prior and Informed Consent (FPIC/CLPI).

## Status

| Module | Source | Count |
|--------|--------|-------|
| Dictionary | BILingo deck (`Lista` + alphabet primer) | 262 entries |
| Encyclopedia | drafted from research (DRAFT-marked) | 14 articles |
| Fauna | Makurap animal vocabulary, photos reused from Bororo/Enawenê by scientific name | 17 (all illustrated) |
| Ethnobotany | Makurap plant vocabulary, reused photos | 7 (3 illustrated) |
| Videos | 6 community oral-history recordings, **self-hosted** MP4 | 6 |
| Bibliography | Braga, Galucio, Maldi, Caspar, Mindlin… | 15 refs |

## Data provenance

- **`raw/`** — the original Makurap material from the NAS: the *BILingo Makurap*
  bilingual learning deck (`*.xlsx`) and its extraction (`makurap_extract.json`).
  The 6 oral-history videos live in **`media/videos/`** (source of truth).
- The dictionary, fauna and ethnobotany files in `data/` are **generated** by the
  scripts in `scripts/` and are git-ignored.
- Fauna/flora photos are **reused** from the sibling platforms
  (`../boeenomoto`, `../enawenenawe`) by matching scientific names — so those
  repos must be present alongside this one at build time.

### Key facts honoured in the content

- "Makurap" is most likely an **exonym of unknown meaning** — stated as such, not invented.
- The descriptive grammar is by **Alzerinda Braga** (1992, 2005); Ana Vilacy
  Galucio's 2001 thesis is on **Mekens**, a sister language (a common misattribution).
- Only the **creation myth** ("O Começo do Mundo", Nambu & Beüd) is from published
  sources; the named video narratives (Payawi, Kaxuléu, castanheira, tucum, pintura)
  are **community oral sources**, not in the public literature, and are flagged as such.
- Tagline **"Ki Mõyen"** ("Nossa Língua") comes from the 2025–26 UNIR documentary
  *Ki Mõyen – Nossa Língua Makurap*.

## Build

```bash
pip install -r requirements.txt   # installs terradoc (+ aptoro + kodudo)
bash scripts/build.sh             # regenerates data, builds site, stages videos
# preview:
python3 -m http.server -d docs 8000   # then open http://localhost:8000
```

The build runs `scripts/prepare_dictionary.py` and
`scripts/prepare_fauna_flora.py`, then `terradoc build`, then copies the videos
from `media/videos/` into `docs/videos/`.

## Theme

Custom **weave** motif (evoking the *marico* tucum-fibre weaving) with a palette
drawn from Makurap material culture: urucum (annatto) red `#B5341F`, tucum-fibre
tan, genipapo near-black, and a green accent.

## Deployment notes (not yet wired)

Intended target: `makurap.terradoc.org` (Cloudflare, via GitHub Actions on push,
like the siblings — see `.github/workflows/build-deploy.yml`). The 6 videos total
~56 MB; for production consider **Git LFS** or external hosting rather than
committing them to the repo. Local prototype only at this stage.
