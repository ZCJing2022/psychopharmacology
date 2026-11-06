# Psychopharmacology

Quarto study site for **PSYC 383 Psychopharmacology**.

The site contains:
- 16 lecture-level Study Guides
- lecture-level Practice Questions with an 80% multiple-choice / 20% written-response mix
- three 50-minute practice exams for each of Parts I, II, and III
- a source-coverage audit
- GitHub Pages deployment through GitHub Actions

## Reproducible build

The generated Quarto source is materialized by:

```bash
python scripts/materialize_site.py
quarto render
```

The expected GitHub Pages URL is:

https://zcjing2022.github.io/psychopharmacology/
