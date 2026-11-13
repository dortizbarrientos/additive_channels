#!/usr/bin/env python3
"""Check result/equation navigation and generate the readable coverage maps.

This checks document navigation and completeness, not the truth of a theorem.
Proofs are in the chapter sources; numerical checks are in the linked scientific
scripts. No third-party Python package is needed.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CHAPTER = dict(conditioning=1, gaussian=2, geometry=3, selection=4,
               inheritance=5, estimation=6, conversion=7, worked=8,
               coverage="A", concepts="B")
TREATMENT = {"proof": "Analytical derivation", "counterexample": "Explicit counterexample",
             "calculation": "Worked or numerical calculation", "estimation": "Statistical procedure",
             "interpretation": "Interpretation", "resource": "Reproduction resource"}


def escape(text):
    """Escape catalogue prose, which is data rather than LaTeX."""
    special = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
               "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}"}
    text = text.replace("–", "--").replace("—", "---")
    return "".join(special.get(c, c) for c in text).replace("²", r"\textsuperscript{2}")


def link(label):
    # Page links work for section, equation, proposition and example labels.
    display = r"Chapter~\ref*{" if label.endswith(":chapter") else r"p.~\pageref*{"
    return r"\hyperref[" + label + "]{" + display + label + "}}"


def equation_maps(equations, label_files):
    """Typeset the audited equation inventory without copying its source texts."""
    count = len(equations["rows"])
    tex = [r"\section{Equation-by-equation map}\label{coverage:equations}",
           f"The following {count} source-qualified equation identifiers connect the main "
           "account and supplementary derivations to this companion. These are stable "
           "source labels, not printed equation numbers. The same label can occur in "
           "different sources. Definitions and model assumptions are identified separately "
           "from proofs and worked calculations. The source versions inspected on "
           + escape(equations["audit_date"]) + " are identified by hashes in "
           + r"\repofile{tutorials/derivations/equation_map.json}{the equation map}. "
           "The map contains identifiers and concepts; the source documents are not needed to build this companion."]
    md = ["# Equation-by-equation derivation map", "",
          f"This map covers **{count} source-qualified equation labels** in the main text, "
          "its mathematical appendices, the visual walkthrough, the mathematics guide "
          "and the worked estimation example. Each points to a definition, analytical "
          "derivation or worked calculation in the companion.", "",
          "The identifiers are stable `eq:` labels in the source, rather than equation "
          "numbers that can change with formatting. The label `eq:Ag` occurs in two "
          "documents, so source identifiers distinguish those entries. The map records "
          "the versions inspected; it does not copy their prose or equation bodies.", "",
          "Open [the PDF](derivations.pdf) for the linked equation map in Appendix A. "
          "The links below open editable chapter sources; each listed label locates "
          "the precise equation, proposition or section within its source.", "",
          "## Treatment of the mapped material", ""]
    for name, meaning in equations["status_legend"].items():
        md.append(f"- **{name.capitalize()}:** {meaning}")
    md += ["", "## Source versions and coverage", "",
           "| Source | Equation labels | Source basename | SHA-256 |",
           "|---|---:|---|---|"]
    for source in equations["sources"]:
        rows = [r for r in equations["rows"] if r["source_id"] == source["id"]]
        md.append(f"| {source['display_name']} | {len(rows)} | `{source['basename']}` | `{source['sha256']}` |")
    md += ["", "The source versions were inspected on **" + equations["audit_date"]
           + "**. The navigation checker validates this recorded inventory and its "
           "companion targets; it does not re-read external source documents or prove the results."]
    for source in equations["sources"]:
        rows = [r for r in equations["rows"] if r["source_id"] == source["id"]]
        tex += [r"\Needspace{8\baselineskip}",
                r"\subsection{" + escape(source["display_name"]) + "}",
                r"\small\begin{longtable}{@{}>{\raggedright\arraybackslash}p{0.28\textwidth}"
                r">{\raggedright\arraybackslash}p{0.47\textwidth}"
                r">{\raggedright\arraybackslash}p{0.16\textwidth}@{}}",
                r"\toprule Source label & Concept and treatment & Derivation\\\midrule\endhead"]
        md += ["", "## " + source["display_name"], "",
               "| Source equation label | Mathematical concept | Treatment | Companion derivation |",
               "|---|---|---|---|"]
        for row in rows:
            targets = row["companion_labels"]
            tex.append(r"\codepath{" + row["equation_label"] + "} & "
                       + escape(row["concept"]) + r"\newline{\footnotesize\itshape "
                       + escape(row["treatment"]) + "} & "
                       + "; ".join(link(t) for t in targets) + r"\\[4pt]")
            sources = "; ".join(f"`{t}` ([source]({label_files[t]}))" for t in targets)
            md.append(f"| `{row['equation_label']}` | {row['concept']} | {row['treatment']} | {sources} |")
        tex += [r"\bottomrule\end{longtable}\normalsize"]
    review = equations["unlabelled_display_review"]
    tex += [r"\subsection{Unlabelled intermediate displays}",
            f"A further {review['total_blocks']} unlabelled displays were inspected. "
            "They supply definitions, intermediate algebra and numerical substitutions "
            "within the derivations above. The machine-readable equation map groups "
            "them by concept and identifies their companion targets; no additional "
            "result was left without a derivation or calculation."]
    md += ["", "## Unlabelled intermediate displays", "",
           f"The review also covered **{review['total_blocks']} unlabelled displays**. "
           + review["method"], "",
           "| Mathematical concept | Companion labels | Coverage note |", "|---|---|---|"]
    for group in review["groups"]:
        targets = "; ".join(f"`{t['label']}` ([source]({label_files[t['label']]}))"
                            for t in group["companion_targets"])
        md.append(f"| {group['concept']} | {targets} | {group['note']} |")
    md += ["", "## Notation between resources", ""]
    md.extend("- " + note for note in equations["notation_notes"])
    md += ["", "The [JSON map](equation_map.json) retains the individual qualifications "
           "and the source metadata. The [result map](RESULT_MAP.md) adds biological "
           "questions and reproduction resources."]
    (HERE / "EQUATION_MAP.md").write_text("\n".join(md) + "\n")
    return tex


def generate(mapping, catalogue, equations, label_files):
    tex = [
        r"\chapter{Result-by-result derivation map}\label{coverage:chapter}",
        "This map covers all 53 records in the existing result catalogue. "
        "Some describe the same mathematics at different locations, and some "
        "describe figures, estimation procedures or teaching resources. They "
        "are not 53 distinct theorems. Each link goes to the appropriate proof "
        "or calculation.",
        r"\section{Analytical results, examples and resources}",
        r"\small\begin{longtable}{@{}p{0.60\textwidth}p{0.32\textwidth}@{}}",
        r"\toprule Result or resource & Derivation or calculation\\\midrule\endhead",
    ]
    md = ["# Derivations, mathematical concepts and biology", "",
          "Every existing catalogue record is mapped below. Open [the PDF](derivations.pdf) "
          "and use its linked result appendix to reach an exact derivation. Chapter numbers "
          "here match that document.", "",
          "| Result | Treatment and chapters | Mathematical concepts | Biological question |",
          "|---|---|---|---|"]
    for r in mapping["results"]:
        title = r["title"]
        if r["result_id"].startswith("appendix_S"):
            title = r["result_id"].replace("appendix_", "Appendix ") + ": " + title
        elif r["result_id"].startswith("main_figure_"):
            title = "Main Figure " + r["result_id"].rsplit("_", 1)[1] + ": " + title
        tex.append(escape(title) + r"\newline{\footnotesize\itshape " + TREATMENT[r["treatment"]]
                   + "} & " + "; ".join(link(s) for s in r["sections"]) + r"\\[4pt]")
        chapters = list(dict.fromkeys(str(CHAPTER[s.split(":")[0]]) for s in r["sections"]))
        md.append("| " + title + " | " + TREATMENT[r["treatment"]] + "; " + ", ".join(chapters)
                  + " | " + "; ".join(r["mathematical_concepts"]) + " | "
                  + r["biological_question"] + " |")
    tex += [r"\bottomrule\end{longtable}\normalsize"]
    tex += equation_maps(equations, label_files)
    tex += [
            r"\section{The eleven interpretation questions}\label{coverage:questions}",
            "The questions in Appendix S6 can be followed through the derivations as follows.",
            r"\begin{description}[style=nextline]"]
    questions = [
        ("Q1: what the share measures", "gaussian:share",
         "A fraction of variance in a quadratic log conditional-mean description under the stated population."),
        ("Q2: established tools and the question addressed", "concepts:chapter",
         "The prerequisite sources and their roles are separated from the comparisons made here."),
        ("Q3: why average before taking logs", "conditioning:jensen",
         "Log conditional mean and conditional mean log are different targets."),
        ("Q4: gene action and a cutoff", "gaussian:share",
         "A population fitness description alone identifies neither gene action nor a universal threshold."),
        ("Q5: which Gaussian assumptions matter", "gaussian:non_gaussian",
         "Third and fourth moments show which identities fail outside the Gaussian model."),
        ("Q6: estimation", "estimation:chapter",
         "Observation and latent-value uncertainty enter the likelihood and refitting procedure."),
        ("Q7: zero gradient and zero variance", "gaussian:singular_support",
         "Zero shares, undefined ratios and reduced-rank supports are treated separately."),
        ("Q8: rankings and selection accuracy", "selection:chapter",
         "Exact weighting and counterexamples distinguish a close fit from an accurate parental prediction."),
        ("Q9: covariance, dimensions and orientation", "geometry:chapter",
         "Whitening, Rayleigh quotients and physical rotation answer different comparison questions."),
        ("Q10: inheritance and equilibrium", "inheritance:chapter",
         "The fixed baseline and retention rule are explicit modelling assumptions."),
        ("Q11: use of the descriptive share", "worked:comparison",
         "Report the share with both absolute components to distinguish different population changes."),
    ]
    for title, target, text in questions:
        tex.append(r"\item[" + escape(title) + "] " + escape(text) + " See " + link(target) + ".")
    tex += [r"\end{description}",
            r"\section{Commands associated with the results}\label{coverage:commands}",
            "Commands start at the repository root. Inputs, outputs and assumptions "
            "remain in " + r"\repofile{reference/result_catalog.json}{the machine-readable catalogue}. "
            "Executing these implementations does not replace the analytical arguments.",
            r"\begin{description}[style=nextline]"]
    for name, command in catalogue["commands"].items():
        # A verbatim block permits long shell commands to remain unambiguous.
        tex.append(r"\item[" + escape(name.replace("_", " ")) + "] "
                   + escape(command["description"]) + "\n"
                   + r"\begin{quote}\small\ttfamily\raggedright\detokenize{"
                   + command["command"] + r"}\end{quote}")
    tex.append(r"\end{description}")
    (HERE / "chapters/09_coverage.tex").write_text("\n\n".join(tex) + "\n")
    (HERE / "RESULT_MAP.md").write_text("\n".join(md) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Regenerate the PDF appendix and Markdown maps.")
    args = parser.parse_args()
    catalogue = json.loads((ROOT / "reference/result_catalog.json").read_text())
    mapping = json.loads((HERE / "result_map.json").read_text())
    equations = json.loads((HERE / "equation_map.json").read_text())
    expected = {r["id"] for r in catalogue["results"]}
    listed = [r["result_id"] for r in mapping["results"]]
    if len(listed) != len(set(listed)) or expected != set(listed):
        raise SystemExit("Result map has missing, duplicate or unexpected catalogue identifiers.")
    label_files = {label: p.relative_to(HERE).as_posix()
                   for p in (HERE / "chapters").glob("*.tex")
                   for label in re.findall(r"\\label\{([^}]+)\}", p.read_text())}
    equation_rows = equations["rows"]
    equation_keys = [(r["source_id"], r["equation_label"]) for r in equation_rows]
    equation_targets = {t for r in equation_rows for t in r["companion_labels"]}
    equation_targets.update(t["label"] for group in equations["unlabelled_display_review"]["groups"]
                            for t in group["companion_targets"])
    source_ids = {s["id"] for s in equations["sources"]}
    equation_errors = {
        "duplicate_equation_keys": len(equation_keys) != len(set(equation_keys)),
        "unknown_sources": sorted({r["source_id"] for r in equation_rows} - source_ids),
        "missing_equation_targets": sorted(equation_targets - set(label_files)),
        "missing_equation_detail": [r["equation_label"] for r in equation_rows
                                    if not r["concept"] or not r["treatment"] or not r["companion_labels"]],
        "inconsistent_source_counts": dict(Counter(r["source_id"] for r in equation_rows))
                                      != equations["summary"]["counts_by_source"],
        "inconsistent_total": len(equation_rows) != equations["summary"]["source_qualified_equation_labels"],
    }
    if any(equation_errors.values()):
        raise SystemExit(json.dumps(equation_errors, indent=2))
    if args.write:
        generate(mapping, catalogue, equations, label_files)
    labels = Counter(label for p in (HERE / "chapters").glob("*.tex")
                     for label in re.findall(r"\\label\{([^}]+)\}", p.read_text()))
    targets = {s for r in mapping["results"] for s in r["sections"]}
    errors = {
        "duplicate_labels": [x for x, n in labels.items() if n != 1],
        "missing_labels": sorted(targets - set(labels)),
        "missing_commands": sorted({x for r in mapping["results"] for x in r["commands"]}
                                   - set(catalogue["commands"])),
        "missing_interpretation": [r["result_id"] for r in mapping["results"]
                                   if not r["mathematical_concepts"] or not r["biological_question"]],
    }
    if any(errors.values()):
        raise SystemExit(json.dumps(errors, indent=2))
    print(json.dumps({"catalogue_records": len(expected), "mapped_records": len(listed),
                      "resolved_derivation_targets": len(targets), "unique_chapter_labels": len(labels),
                      "source_qualified_equations": len(equation_rows),
                      "equation_derivation_targets": len(equation_targets),
                      "audited_unlabelled_displays": equations["unlabelled_display_review"]["total_blocks"],
                      "mathematical_concepts_and_biology_present": True, "status": "passed"}, indent=2))


if __name__ == "__main__":
    main()
