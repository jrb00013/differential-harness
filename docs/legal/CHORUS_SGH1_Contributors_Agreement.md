# CHORUS-SGH-1 Contributors Agreement

**Project:** differential-harness — CHORUS-Skid **SGH-1** + **AEH-1**  
**Program:** CHORUS Research Program  
**Principal lead:** Joseph Black  
**Effective template date:** 2026-06-01  
**Repository:** `differential-harness` (GitHub / private distribution as applicable)

---

> **Disclaimer:** This document is a **project governance template**, not legal advice. Before signing, funding, filing patents, or taking investment, have a qualified attorney review it for your jurisdiction and entity structure.

---

## 1. Purpose

This agreement defines how people contribute to the **CHORUS-SGH-1** bench skid (pressure-retarded osmosis + anthropogenic brine pairing + acoustic energy harvest / ultrasonic assist + shared DAQ), how **credit** is recorded, and how **intellectual property** is handled relative to open-source code and separate patent / commercial tracks.

## 2. Definitions

| Term | Meaning |
|------|---------|
| **Project** | The `differential-harness` repository and related hardware, simulation, DAQ, documentation, and research outputs for SGH-1 / AEH-1. |
| **Principal lead** | Joseph Black — originator of the integrated CHORUS-SGH-1 architecture and default coordinator for filings, publications, and external outreach unless reassigned in writing. |
| **Contributor** | Any individual or organization that merges work, supplies data under this agreement, or signs below. |
| **Substantive contribution** | Original work that is more than typo fixes: simulation modules, CAD parts, bench protocols, experimental datasets, claim-relevant design choices, or major documentation that advances reduction-to-practice. |
| **Entity** | The legal person that will own filed patents and commercial licenses (e.g. **CHORUS Research Program**, an LLC, or university — fill in before signatures). |

## 3. What you may contribute

Contributions include, without limitation:

- **Software:** Python simulation (`simulation/`), DAQ (`daq/`), notebooks, paper pipeline scripts  
- **Hardware:** OpenSCAD / STL, BOM lines, wiring, build and test protocols  
- **Research:** Figures, calibration JSON, bench CSVs, manuscript sections  
- **Operations:** Lab time, machining, sensors, hosting, grant administration  

Each contribution should be tied to a **dated record**: git commit, inventor-notebook entry (see `docs/INVENTOR_NOTEBOOK.md`), and/or signed exhibit list (Appendix A).

## 4. Open-source license (code & docs)

Unless marked otherwise in the file header:

1. **Repository code and docs** are contributed under the **MIT License** (or the license stated in the repo root at time of merge).  
2. You represent that you have the right to contribute the material and that it does not knowingly violate third-party rights.  
3. **Pre-existing IP:** List any background patents, designs, or code in **Appendix B**. Background IP stays yours; you grant the Project a non-exclusive license to use it only as embedded in your contribution.

## 5. Credit tiers (how we split “credit”)

Credit is **not one-size-fits-all**. Different outputs use different rules.

### 5.1 Tier summary

| Tier | Typical role | Where credited | How earned |
|------|----------------|----------------|------------|
| **A — Principal lead** | Architecture, program direction | Cover page, patent lead contact, “corresponding author” on flagship paper | Joseph Black (unless transferred by written amendment) |
| **B — Co-inventor** | Conception / reduction to practice on **patent claims** | USPTO inventor list on filed applications | Substantive contribution to **at least one claim** (US inventorship rules); see §6 |
| **C — Publication author** | Analysis, writing, experiments | Research PDF / journal byline | Substantive work on **that publication** (ICMJE-style adapted); order negotiated before submission |
| **D — Repository contributor** | Merged PRs, CAD, tooling | `CONTRIBUTORS.md`, release notes, optional “Contributors” section in compendium PDF | Merged contribution + name in Appendix A |
| **E — Acknowledgment** | Funding, facilities, review | “Acknowledgments” in papers and decks | No IP claim; name only |

### 5.2 Publication authorship (default policy)

For the flagship report *CHORUS-SGH-1: Brine-Gradient Power on a Bench Skid* and derivative papers:

1. **First / corresponding author:** Principal lead unless all co-authors agree otherwise in writing before submission.  
2. **Co-authors:** Must (a) contribute to design, analysis, or drafting, and (b) approve the final manuscript.  
3. **Author order** after the lead: by **negotiated** contribution (weighted: new physics/analysis > hardware build > software plumbing > editorial).  
4. **Guest / honorary authorship is not permitted.**

### 5.3 Engineering & repo attribution

- **CAD parts:** Credit in `hardware/COMPONENT_INDEX.md` and commit history; major new subsystems get a line in release notes.  
- **Simulation:** Module docstring + `exports/paper_experiments.json` provenance when applicable.  
- **Bench data:** CSV metadata (`data/bench/*.meta.json`) lists operator, date, and contributors.

## 6. Patent inventorship & ownership

Patent credit follows **US law (and equivalent rules elsewhere):** inventors are natural persons who contributed to the **conception** of at least one claim, not sponsors or “project managers” alone.

### 6.1 Default claim buckets (SGH-1)

Align contributions to these focus areas from `docs/SGH1_PATENT_AND_DEPLOYMENT.md`:

1. Integrated skid: PRO + CHOR plenum + AEH panel + shared DAQ bus  
2. Anthropogenic brine + low-sal feed pairing on modular manifold  
3. ΔP/Δπ feedback using dual conductivity sensors  
4. Dual-mode acoustic: harvest + ultrasonic CP assist  

**Co-inventor** status requires documented input to one or more of these **before** public disclosure (conference, arXiv, open repo without NDA, etc.).

### 6.2 Ownership & assignment

- Filed patents are owned by **Entity:** _____________________________  
- Contributors who qualify as inventors **assign** their patent rights to Entity (or agree to cooperate in filing) via signature below.  
- Entity agrees to **credit all named inventors** on filings and to negotiate revenue share per §7.

### 6.3 Disclosure duty

Contributors must **promptly disclose** prior publications, patents, or public talks that might be prior art. Do not commit claim-critical ideas to public repos until provisional strategy is confirmed with the lead.

## 7. Commercial & revenue split (if monetized)

If the Project generates **licensing revenue, grants allocated to commercialization, or acquisition proceeds** tied to SGH-1 IP, default **negotiation starting point** (adjust before signing):

| Stakeholder pool | Suggested share of net revenue* | Notes |
|------------------|----------------------------------|-------|
| **Principal lead** | **40%** | Program risk, architecture, coordination |
| **Co-inventors (pool)** | **35%** | Split **equally** among named inventors on the issued patent(s) |
| **Key contributors (non-inventor pool)** | **15%** | Split by written **Contribution Points** (Appendix C) |
| **Entity / reserve** | **10%** | Legal, filing fees, future R&D |

\* *Net* = gross receipts minus direct licensing costs, filing maintenance, and agreed entity overhead (define in entity operating agreement).

**Contribution Points (Appendix C)** — example weights (lead assigns at milestone review):

| Activity | Points |
|----------|--------|
| New claim-relevant subsystem conceived + documented | 10 |
| Reduction-to-practice bench result (positive power or key metric) | 8 |
| Major simulation / sizing module | 5 |
| Production CAD + BOM for build | 4 |
| DAQ / automation enabling publishable dataset | 3 |
| Sustained review + integration (6+ months) | 2 |

Pools are **renegotiated** when a new co-inventor joins or at each provisional / non-provisional filing.

## 8. Confidentiality & NDAs

- **Public repo** content is not confidential once merged to default branch.  
- **Bench data, investor decks, and pre-filing designs** may be shared under a separate NDA — do not forward without lead approval.  
- Outreach package per patent playbook: 1-pager + design report + data **under NDA** until counsel approves otherwise.

## 9. Representations

Each contributor represents that:

1. Their contribution is their own work (or properly licensed).  
2. They will not intentionally introduce malware or fabricated data.  
3. They will abide by lab safety and export control rules applicable to their site.  

## 10. Term & withdrawal

- This agreement applies from the **signature date** forward to contributions made while participating.  
- Withdrawal: written notice to the lead; **prior licenses and assignments survive** for work already merged or filed.  
- Removal from inventor list after filing requires counsel — do not unilaterally edit patent records.

## 11. Dispute resolution

1. **Good-faith negotiation** between contributor and principal lead (14 days).  
2. **Mediation** in __________________ (city/state) if unresolved.  
3. Litigation only as a last resort; prevailing-party fees only if required by entity bylaws.

## 12. Signatures

By signing, you agree to this template as amended by **Appendix A–C** for your role.

| Role | Printed name | Entity (if any) | Signature | Date |
|------|--------------|-----------------|-----------|------|
| Principal lead | Joseph Black | CHORUS Research Program | | |
| Contributor | | | | |
| Contributor | | | | |
| Entity representative | | | | |

---

## Appendix A — Contribution log (exhibit)

| Date | Contributor | Description (commit / notebook / part) | Tier (B–E) |
|------|-------------|------------------------------------------|------------|
| | | | |

---

## Appendix B — Background IP disclosure

| Contributor | Description of pre-existing IP | License to Project |
|-------------|------------------------------|--------------------|
| | | |

---

## Appendix C — Contribution points ledger

| Contributor | Points | Milestone / notes |
|-------------|--------|-------------------|
| | | |

---

## Quick reference: “How do we split credit?”

| Question | Answer |
|----------|--------|
| **GitHub / repo fame?** | Tier D — merged work + `CONTRIBUTORS.md` + Appendix A |
| **Paper byline?** | Tier C — negotiate before submit; lead is default corresponding author |
| **Patent name on filing?** | Tier B only — real inventorship per §6; no “gift” inventors |
| **Money from a license?** | §7 pools — inventors split 35%; lead 40%; points pool 15% |
| **Who decides disputes?** | Lead first, then mediation (§11) |

---

*Generated from project template · Build PDF: `./scripts/build_contributors_agreement.sh`*
