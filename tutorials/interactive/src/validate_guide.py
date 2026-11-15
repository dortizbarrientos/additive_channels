"""Check the assembled offline guide and its checked scientific sources."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlparse

from lxml import html

from reference_integrity import validate_reference

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent
REPO = HERE.parents[2]
GUIDE = MODULE / "Additive_channels_interactive_guide.html"
LESSONS = ["counts", "share", "population", "selection", "estimation", "inheritance"]
LABS = [
    "counts-lab", "share-lab", "population-lab", "geometry-lab", "selection-lab",
    "estimation-lab", "bootstrap-lab", "quartic-lab", "inheritance-lab",
]
SOURCE_PREFIX = "/dortizbarrientos/additive_channels/blob/main/"


def main():
    raw = GUIDE.read_bytes()
    tree = html.fromstring(raw)
    ids = Counter(tree.xpath("//@id"))
    assert all(count == 1 for count in ids.values()), "Duplicate HTML IDs"
    articles = tree.xpath("//article[contains(concat(' ', @class, ' '), ' lesson ')]")
    assert [a.get("id") for a in articles] == ["home"] + LESSONS
    assert all(ids[lab] == 1 for lab in LABS), "Missing teaching control placeholder"

    # Reading and calculation use only code, styles and records inside the file.
    assert not tree.xpath("//script[@src] | //link[@href] | //iframe | //object | //embed")
    assert not tree.xpath("//img[@src] | //audio[@src] | //video[@src] | //source[@src]")
    styles = "\n".join(tree.xpath("//style/text()"))
    assert not re.search(r"@import|url\(\s*['\"]?(?:https?:|//)", styles, re.I)

    embedded = tree.xpath("//script[@id='scientific-reference']/text()")
    assert len(embedded) == 1
    record = json.loads(embedded[0])
    assert record == json.loads((HERE / "scientific_reference.json").read_text())
    source_report = validate_reference(record)

    checked_links = 0
    for href in tree.xpath("//a/@href"):
        if href.startswith("#"):
            assert unquote(href[1:]) in ids, f"Missing HTML target: {href}"
            continue
        parsed = urlparse(href)
        if parsed.netloc == "github.com" and "/dortizbarrientos/additive_channels/" in parsed.path:
            assert parsed.path.startswith(SOURCE_PREFIX), f"Non-current source link: {href}"
            relative = unquote(parsed.path[len(SOURCE_PREFIX):])
            assert not relative.startswith("tutorials/derivations/"), href
            assert (REPO / relative).is_file(), f"Missing repository source: {relative}"
            checked_links += 1
        elif not parsed.scheme:
            assert (MODULE / unquote(parsed.path)).exists(), href

    scripts = "\n".join(
        tree.xpath("//script[not(@src) and not(@type='application/json')]/text()")
    )
    syntax = subprocess.run(
        ["node", "--check"], input=scripts, text=True, capture_output=True,
    )
    assert syntax.returncode == 0, syntax.stderr

    report = {
        "all_checks_passed": True,
        "html_sha256": hashlib.sha256(raw).hexdigest(),
        "lesson_count": len(LESSONS),
        "teaching_control_placeholders": len(LABS),
        "repository_source_links_checked": checked_links,
        "embedded_reference_matches": True,
        "external_runtime_assets": 0,
        "javascript_syntax_valid": True,
        "scientific_reference": source_report,
        "scope": "Checks offline packaging, structure, source links and scientific provenance; does not render a browser.",
    }
    (HERE / "guide_validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
