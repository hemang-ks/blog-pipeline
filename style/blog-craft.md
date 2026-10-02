# blog-craft.md
_Last updated: 2026-10-02_
Approved: 2026-10-02

This extends [writing-rules.md](writing-rules.md). It doesn't repeat those rules — it covers what's specific to a blog post: structure, headlines, mode, and the techniques worth stealing from the exemplars.

---

## 1. Reader and promise

Hemang's readers are practitioners, not a general tech audience: platform leads, architects, and technical decision-makers at large organizations — mostly Financial Services, Healthcare, and Public Sector — who are past the demo stage and stuck on the harder problem of running AI in production. They already know what an LLM is. They don't need the basics explained.

Every post has to leave them knowing something specific they didn't know before: a mechanism that explains a failure they've seen, a tradeoff clarified with evidence, or a judgment call they can argue with because it's concrete enough to argue with. Not inspiration. Not a product pitch. A sharper model of the problem, usable on their own systems this week.

---

## 2. Shared craft rules

**Headlines.** Three patterns:
- *The reversal.* States a belief and flips it. "Why your GPU utilization graph is lying to you."
- *The forced choice.* Frames a real decision the reader is facing. "Fine-tune or retrieve: which one actually solves your problem?"
- *The named mechanism.* Puts the insight in the title as a noun phrase. "KV-cache-aware routing: the optimization most clusters skip."

**Openings.** First three sentences: a concrete scene, a failure, or a claim. No throat-clearing, no scene-setting about the state of the industry. Start where the problem starts.

**TL;DR.** Use one for technical posts over ~1,200 words — readers skimming for the payload deserve it up front. Skip it in strategy mode; a news hook followed by a TL;DR undercuts the arc that makes the piece worth reading.

**Section headings are claims.** "Architecture" tells the reader nothing. "The scheduler, not the GPU, was the bottleneck" tells them what to expect and why it matters.

**The one story rule.** At most one `[ME:…]` story per post. Zero is fine. Never invent one. If nothing's recorded, use a cited case from the sources or a stated position — phrased as judgment, never as something that happened to you.

**The counterpoint.** Present the strongest real version of the objection, attributed to whoever actually holds it, then answer it with evidence. A strawman counterpoint is worse than no counterpoint.

**Endings.** A sharp implication or a concrete next step — something the reader can go check in their own system. Never a recap of what you just told them.

**Platform limits.** No Markdown tables — convert to a short list, or flag the spot for an image. No Mermaid. No footnote syntax; use `[S#]`/`[W#]` markers, which export turns into linked numbers.

---

## 3. Mode: technical

Target: **1,200–2,000 words.** Both technical exemplars ran shorter (4–5 minute reads), but Hemang's posts go one layer deeper into tradeoffs and operational detail, so the range runs a bit longer.

**Structure:** concrete failure or problem → the one mechanism that explains it → tradeoffs, stated honestly → a short worked example or single pseudocode block → what this means for the reader's own deployment.

**Code.** One block maximum. It should illustrate the mechanism, not be a working implementation. Fenced code blocks are skipped by lint, so they're exempt from the citation and style rules that apply to prose.

**Honesty about uncertainty.** Separate what's confirmed, what's reasonably inferred, and what's your own read — explicitly. If something is undisclosed or unmeasured, say so instead of smoothing over it. Inferred architecture is useful; inferred architecture presented as settled fact is not.

**Depth.** Don't assume the reader already holds every prerequisite concept. When a claim is genuinely dense — a specific caching strategy, a scheduling algorithm — add one sentence of "what this means in practice" before moving on. Slow down exactly where the reader would otherwise have to re-read.

---

## 4. Mode: strategy

Target: **2,000–3,000 words**, up to 3,500 when the evidence earns it. The strategy exemplar ran about 3,000 words; Hemang's own version should run tighter and less journalistic.

**Structure:** a news hook or event → why the earlier approach made sense at the time → what specifically changed → evidence for the change (metrics, named sources, dated quotes) → what it means for the reader → optionally, the broader lesson beyond this one case.

**History before judgment.** Establish the original constraint and show the old decision actually worked for a while. Don't frame a past choice as simply wrong in hindsight — that's a lazy version of the story and it's less credible.

**Evidence over assertion.** Use specific, attributed numbers and quotes when sources provide them. A vague claim that something "naturally" performs better is weaker than one measured figure.

**Comparisons without tables.** State the delta directly in a sentence, or use a short before/after list. Save genuinely visual comparisons for a flagged image spot.

---

## 5. Mode selection (for `/blog-research` when mode = auto)

**Technical signals:** the thesis is falsifiable by a benchmark, a log, or a config change. The audience's question is "how does this work" or "why did this break." The payload is a mechanism.

**Strategy signals:** the thesis is falsifiable only by watching a bet play out over quarters. There's a clear "why now" — a reversal, an announcement, a market shift. The audience's question is "what does this mean for my decisions," not "how do I implement this."

When intake.md doesn't force a mode, default to whichever question the sources actually answer.

---

## 6. Techniques observed in the exemplars

- **Cold open on failure (E1).** Opens with a specific thing going wrong, not a definition. The architecture that follows is framed as the fix.
- **Single-mechanism spine (E1).** One loop structures both the system being described and the article describing it — every section maps to one step.
- **Claim-first TL;DR (E2).** The summary states conclusions as numbered claims, not topics — it compresses the payload instead of previewing the outline.
- **Confidence labeling (E2).** Repeatedly marks what's confirmed versus inferred versus undisclosed, including naming the specific things that aren't publicly known.
- **Concretize the abstraction (E2).** Pairs an abstract mechanism with a specific operational example immediately, so the concept has something to attach to.
- **Constraint, then reversal (E3).** Establishes why the original choice was reasonable before explaining why it changed — earns the reversal instead of asserting it.
- **Named-source evidence (E3).** Attributes specific metrics and quotes to named people in named roles, dated, instead of summarizing secondhand.
- **Zoom-out close (E3).** Ends by lifting the single case to a broader question the reader can apply elsewhere.

---

## 7. Anti-patterns specific to posts

- **The generic AI-blog shape.** What is X → Benefits → Architecture → Best Practices → Conclusion. If a post could have been generated from the product docs, it's missing a point of view.
- **Inference creeping into fact.** Reasonable speculation about an undisclosed system is fine; letting it read as confirmed two paragraphs later is not.
- **Tables as a crutch.** A table of pros and cons is often a paragraph that hasn't been written yet.
- **A TL;DR that just previews the outline.** It should compress the answer, not list the section headers.
- **An unanonymized or over-specific `[ME]` story.** No client names, no numbers precise enough to identify an engagement.
- **Side-story bloat.** Historical examples are useful only if they move the thesis forward. Cut the ones that are just interesting.
- **A strawman counterpoint.** If the objection is easy to dismiss, it's not the real objection.
