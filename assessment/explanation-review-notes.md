# Explanation expansion: scope, validation, and assessment cautions

## What this revision changes

This is an **Explanation-only revision** of the Psychopharmacology practice material at repository commit `b17ab33a554fed296a0b0fba07c69c36b06132f6`. It supplies 410 individually authored explanations and applies them to all 749 question appearances: 16 lecture banks and nine practice exams. Each explanation gives substantive conceptual reasoning, normally in two paragraphs, followed by source context and a study-guide link. Narrative length is 99–157 words, excluding references.

The update preserves question stems, choices, answer keys/model answers, numbering, anchors, page order, exam formats, and initially collapsed Answer and Explanation panels. Matching questions in an exam and a lecture bank use the same explanation. The source files supplied by the user are the basis; this is not a current clinical-guideline update or medical advice.

## Important limitations of the existing questions

The original bank contains **30 distinct questions with placeholder answer text** beginning “The lecture treats …”; these appear **67 times** across lecture banks and exams. Other items contain headings, figure labels, or administrative slides as answer text. Adding an explanation does not convert these into valid multiple-choice questions. In addition, many original MCQs ask which statement matches a slide topic while offering other true lecture statements as distractors; their uniqueness and assessment value need a separate question-writing review.

Where the existing key is a placeholder, unsupported claim, or conflicts with the supplied evidence, the new Explanation states the limitation rather than endorsing it. **The unchanged keys must not be treated as newly validated.** These materials are for formative study; instructor review is needed before formal grading.

## Source hierarchy and gaps

Lecture presentations define the course topic and emphasis; the assigned Meyer chapters supply supporting mechanisms. Source notes identify the original lecture topic's PDF-page anchor, not a claim that every explanatory sentence comes from that single slide. All page numbers refer to PDF pages, not printed textbook page numbers.

Lecture 11 has a presentation but no assigned Meyer chapter. Lecture 16 has Chapter 13 and Web Boxes but no lecture presentation; the explanation notes therefore cite Chapter 13 and do **not** repeat the original bank's synthetic lecture-page labels. The Lecture 13 folder assigns Chapter 9; explanations of stimulant-specific mechanisms also draw explicitly on Chapter 12 of the supplied full textbook. Study-guide links are retained as navigation aids, not evidence that the study guides themselves have been revised or validated.

## Priority instructor-review items

| Question(s) | Issue made explicit in the expanded explanation |
|---|---|
| L03-MC19; L10-MC14–15; selected Lecture 11 orientation items | Promotional, exam-administration, or heading-only material is not a substantive scientific assessment. |
| L05-MC11; L07-MC01/MC20/SA05 | The dopamine-deficient model requires the specified restoration of tyrosine hydroxylase in DBH-expressing cells; intact DBH alone does not explain preserved noradrenaline. |
| L06-MC13; L13-MC26 | Transporter reversal must be distinguished from receptor inverse agonism. The terminology in the original key is not silently endorsed. |
| L08-MC16/SA03 | The tonic/phasic acetylcholine and transfer account is a lecture hypothesis, not established merely by naming the proposed mechanism. |
| L09-MC05 | Transporters move glutamate; glutamine synthetase performs its conversion to glutamine. |
| L09-MC06 | The lecture's cerebrum/parallel-fiber wording differs from the textbook's cerebellar account. |
| L09-MC08 | The lecture's astrocytic D-serine account differs from Chapter 8's emphasis on neuronal formation. |
| L09-MC14 | Depolarization relieves the NMDA channel's magnesium block; it does not simply permit glutamate to bind. |
| **L09-MC17/SA04** | **Lecture and textbook disagree on the necrosis/apoptosis timing statement. The original timing-based key is not reliable as written.** |
| **L13-MC19** | **The supplied graph/textbook show different directions for D2 and D3 antagonist effects on cocaine-related locomotion. The original key's statement that both are required overstates the evidence.** |
| L14-MC04 | An imprecise alcohol-clearance rule is not a safe calculator for sobriety or driving. |
| L15-MC11–12 | A food-reward diagram and a thalamic abbreviation have source/label limitations; their claims are not expanded into established pathways. |
| L15-MC14 | A vague prevalence claim does not establish that most medically treated patients develop addiction; dependence and addiction are distinguished. |
| **All Lecture 16 questions** | **No lecture presentation was supplied. All ten existing answer/model-answer entries contain placeholders; the substantive new discussion is explicitly textbook-based.** |

These are selected priority issues, not a claim that every original question has undergone a complete assessment-quality audit. The explanations also qualify historical approval/prevalence claims, distinguish animal tasks from human diagnoses, and separate experimental evidence from proposed mechanisms.

## Deployment persistence

The existing publishing workflow rematerializes the original site from `scripts/materialize_site.py` on every run. Editing `practice/*.qmd` alone would therefore be overwritten. The installer inserts an `Apply detailed explanations` step **after materialization and before the existing commit/render steps**. It uses `scripts/apply_explanations.py` and `assessment/detailed-explanations.json` to reapply the authored text.

The patcher validates every question's heading, stem/options, and answer content before writing any page. Only Explanation bodies are replaced. If a question changes, the patcher stops instead of attaching an explanation to a different question. The data JSON must then be reviewed and updated deliberately; do not bypass that check. Re-running against an already updated site is a no-op.

## Verification boundary

The delivered package includes local structural and application tests, unchanged-content checks, and an independent browser-readable preview. The current session cannot push commits to GitHub. Quarto is not installed in the working environment, so the complete updated Quarto build and live GitHub Pages deployment have **not** been performed here. The repository's existing workflow performs that render after the user commits and pushes the installed update.
