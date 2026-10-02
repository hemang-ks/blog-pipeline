# Lint calibration — exemplars
_Generated 2026-10-02 by running `blog lint` against each exemplar corpus file._

E1 and E2 have no corpus text (Medium blocked both with a 403 bot wall — see M2.2). This calibration covers **E3** only (`style/exemplars/corpus/S3-why-has-shopify-dropped-react-native.md`, mode: strategy). Revisit when a technical-mode exemplar with real text is available.

## Hits per rule (E3, 142 findings total)

| Rule | Severity | Count | Recommendation |
|---|---|---|---|
| `exemplar_overlap` | hard | 80 | **Calibration artifact, not a signal.** Linting an exemplar against its own corpus directory trivially 100%-overlaps every long sentence with itself. This rule is only meaningful for linting a *draft*, not for linting the exemplar it's calibrated against. Keep as hard; ignore this count. |
| `citations:unmarked_number` | soft | 32 | Keep soft. E3 is journalism, not a blog-pipeline post — it wasn't written with `[S#]`/`[W#]` markers at all, so every stat trips this. The rule is correct; the high count just reflects a style mismatch between the exemplar's own citation convention and ours. |
| `citations:unmarked_quote` | hard | 8 | Keep hard, with one caveat below (see "leveraging"). All 8 are real interview quotes without markers — exactly what this rule should catch in our own posts. |
| `structure:rule_of_three` | soft | 5 | Keep soft. Checked the hits — these are genuine enumerations (e.g., named lists of three real things), not fabricated adjective triplets. A blunt pattern-matcher will always have some false-positive rate here; soft is the right tier. |
| `banned-word:very` | soft | 4 | Keep soft. Even well-edited published writing uses filler emphatics occasionally. Confirms soft (not hard) is correctly calibrated — if this were hard, a piece you picked as an exemplar would fail lint. |
| `banned-word:quite` | soft | 3 | Same as `very` — keep soft. |
| `structure:max_paragraph_sentences` | soft | 3 | Keep soft. All three hits are long quoted speech, where normal paragraph-length conventions don't apply. |
| `structure:same_length_run` | soft | 2 | Keep soft. Low count, expected heuristic noise. |
| `banned-word:leveraging` | hard | 1 | **Worth a decision.** The one hit is inside a direct quote from Shopify's own blog post ("our strategy of leveraging RN"), not the author's prose. The lint engine doesn't currently exempt banned words inside quoted/attributed material — sanitizing a quote would misrepresent what the source actually said. Recommend adding a carve-out: skip hard/soft word-and-phrase checks inside quoted spans that carry a citation marker (same exemption `source_overlap` already gets). Not implemented yet — flagging for your call. |
| `banned-word:ecosystem` | soft | 1 | Keep soft. Single hit, non-filler usage ("mobile ecosystem"). |
| `banned-word:comprehensive` | soft | 1 | Keep soft. Single hit. |
| `structure:bold_per_300_words` | soft | 1 | Keep soft. E3 bolds pull-quotes from interviews, a different convention than emphasis-for-emphasis's-sake. |
| `confidential:missing_file` | info | 1 | Expected — `style/confidential.yaml` doesn't exist on this machine yet (M2.6, Me-owned). Not a failure. |

## Overall read

Nothing here suggests the hard/soft split is miscalibrated. The one real finding — banned words inside direct quotes — isn't a hard/soft question, it's a missing exemption. Recommend: exempt quoted-and-marked spans from word/phrase checks the same way `source_overlap` already exempts them, so quoting a source accurately never trips lint. Your call whether to fix that now or carry it as a known gap into M2.4 review.
