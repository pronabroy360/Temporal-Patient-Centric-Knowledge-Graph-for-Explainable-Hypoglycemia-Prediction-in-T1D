#!/usr/bin/env python3
"""Build the bounded 2026-10-31 manuscript from existing aggregate evidence.

No model training, participant-level reads, or bootstrap recomputation occurs.
Only this manuscript directory receives generated outputs.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import struct
import sys
import zipfile
from pathlib import Path
from statistics import mean
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SNAPSHOT = "2026-10-31"
MANIFEST = "69b41e4acfae7d2afc990c8cd15d8fc3f969784d4e5f6534a9263033d341ad52"
INPUT_CONTENT = "3c142f9e6fbeeac7afbb30bb745f67593fad1282c0463dd9a8a5b15314af4c28"
sources = {}


def read_json(relative):
    path = ROOT / relative
    payload = path.read_bytes()
    sources[str(relative)] = {"sha256": hashlib.sha256(payload).hexdigest(),
                              "bytes": len(payload)}
    return json.loads(payload)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def near(a, b):
    return math.isclose(a, b, abs_tol=1e-12, rel_tol=0)


def fmt(value, signed=False):
    return f"{value:+.6f}" if signed else f"{value:.6f}"


def estimate(metric):
    return (f"{fmt(metric['difference_first_minus_second'], True)} "
            f"({fmt(metric['difference_ci95'][0], True)}, "
            f"{fmt(metric['difference_ci95'][1], True)})")


def md_table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |",
                      "| " + " | ".join("---" for _ in headers) + " |",
                      *["| " + " | ".join(map(str, row)) + " |" for row in rows]])


def collect_pairs():
    pairs = []
    for seed, folds, date in [(20261003, range(5), "20261019"),
                              (20261004, range(5), "20261020")]:
        for fold in folds:
            suffix = "" if seed == 20261003 else f"_seed{seed}"
            name = f"audit/loop_mps_outer{fold}{suffix}_graph_vs_sequence_paired_{date}.json"
            paired = read_json(name)
            contract = paired["training_contract"]
            require(contract["seed"] == seed and contract["fold"] == f"outer-{fold}",
                    f"Training seed/fold mismatch: {name}")
            require(paired["draws"] == 10000, f"Unexpected bootstrap count: {name}")
            require(paired["manifest_sha256"] == MANIFEST, "Manifest mismatch")
            require(set(paired["parameter_counts"].values()) == {36883}, "Parameter mismatch")
            require(contract["epochs"] == 1 and contract["batch_size"] == 4096,
                    "Budget mismatch")
            for archive_key, side, variant in [
                ("first_archive", "first", "graph-generic"),
                ("second_archive", "second", "history-event-capacity-matched")]:
                result = read_json(str(Path(paired[archive_key]) / "result.json"))
                require(result["complete"] is True and result["prediction_identity_verified"] is True,
                        "Incomplete or unverified local run")
                require(result["locked_holdout_used"] is False, "Unexpected holdout use")
                require(result["variant"] == variant, "Unexpected model variant")
                require(result["trainable_parameters"] == 36883, "Run parameter mismatch")
                for key in ["seed", "fold", "epochs", "batch_size", "workers", "history_steps",
                            "max_events", "input_content_sha256", "training_membership_sha256",
                            "train_windows_expected", "train_positive_labels_expected",
                            "manifest_sha256", "window_identity_sha256", "metric_version"]:
                    require(result[key] == contract[key], f"Run contract mismatch: {key}")
                for key in ["name", "learning_rate", "weight_decay", "loss"]:
                    require(result["optimizer"][key] == contract["optimizer"][key],
                            f"Optimizer mismatch: {key}")
                metrics = result["groups"]["validation"]
                for key in ["participants", "windows", "positive_labels"]:
                    require(metrics[key] == paired[key], f"Validation count mismatch: {key}")
                require(metrics["prediction_window_identity_sha256"] ==
                        contract["prediction_window_identity_sha256"], "Window identity mismatch")
                for output, metric in [("participant_macro_ap", "participant_macro_ap"),
                                       ("participant_macro_brier", "participant_macro_brier"),
                                       ("pooled_brier", "pooled_brier")]:
                    require(near(metrics[output], paired[metric][side]), "Point estimate mismatch")
            for key in ["participant_macro_ap", "participant_macro_brier"]:
                metric = paired[key]
                require(near(metric["first"] - metric["second"],
                             metric["difference_first_minus_second"]), "Difference arithmetic mismatch")
                lo, hi = metric["difference_ci95"]
                require(lo <= metric["difference_first_minus_second"] <= hi, "Malformed interval")
            paired["manuscript_source"] = name
            pairs.append(paired)
    return pairs


def figures(pairs):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MultipleLocator
    destination = HERE / "figures"
    destination.mkdir(exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "svg.fonttype": "none", "pdf.fonttype": 42})
    fig, ax = plt.subplots(figsize=(7.2, 4.6), layout="constrained")
    for seed, color, marker, offset in [(20261003, "#17627b", "o", .10),
                                        (20261004, "#b96922", "s", -.10)]:
        group = [p for p in pairs if p["training_contract"]["seed"] == seed]
        points = [p["participant_macro_ap"]["difference_first_minus_second"] for p in group]
        lower = [v - p["participant_macro_ap"]["difference_ci95"][0]
                 for p, v in zip(group, points)]
        upper = [p["participant_macro_ap"]["difference_ci95"][1] - v
                 for p, v in zip(group, points)]
        positions = [4 - int(p["training_contract"]["fold"][-1]) + offset for p in group]
        ax.errorbar(points, positions, xerr=[lower, upper], fmt=marker, capsize=3,
                    color=color, markersize=6, label=f"Seed {seed}", lw=1.5)
    ax.axvline(0, color="0.5", lw=.8, linestyle="--")
    ax.set(yticks=range(5), yticklabels=[f"Fold {i}" for i in reversed(range(5))],
           xlim=(-.005, .13), ylim=(-.6, 4.6),
           xlabel="Graph − sequence: participant-macro average precision")
    ax.xaxis.set_major_locator(MultipleLocator(.02))
    ax.grid(axis="x", alpha=.17)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.legend(loc="lower right", frameon=False, fontsize=9)
    for suffix in ["png", "pdf", "svg"]:
        fig.savefig(destination / f"ap_differences.{suffix}", dpi=240)
    svg = destination / "ap_differences.svg"
    svg.write_text(re.sub(r"[ \t]+(?=\n)", "", svg.read_text()))
    plt.close(fig)


def blocks(markdown):
    lines = markdown.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line.startswith("|"):
            rows = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                cells = [cell.strip() for cell in lines[index].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", cell) for cell in cells):
                    rows.append(cells)
                index += 1
            yield "table", rows
            continue
        match = re.fullmatch(r"!\[(.*?)\]\((.*?)\)", line)
        if match:
            yield "image", (match[1], match[2])
        elif line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            yield "heading", (level, line[level:].strip())
        else:
            paragraph = [line]
            while index + 1 < len(lines) and lines[index + 1].strip():
                if lines[index + 1].startswith(("#", "|", "![")):
                    break
                index += 1
                paragraph.append(lines[index].strip())
            yield "paragraph", " ".join(paragraph)
        index += 1


def normalize_references(markdown):
    """Order numeric references by first citation and reject dangling citations.

    Template labels stay stable for editing. Only cited references appear in
    the generated main paper; the full study bibliography remains in BibTeX.
    """
    body, reference_text = markdown.split("## References", 1)
    legends = ""
    if "## Figure legends" in reference_text:
        reference_text, legends = reference_text.split("## Figure legends", 1)
    reference_rows = re.findall(r"(?m)^\[(\d+)\]\s+(.+)$", reference_text)
    references = {int(number): text for number, text in reference_rows}
    require(len(reference_rows) == len(references), "Duplicate bibliography labels")
    mapping = {}

    def replace(match):
        numbers = []
        for group in match.group(1).split(","):
            bounds = re.split(r"[–-]", group.strip())
            if len(bounds) == 2:
                start, end = map(int, bounds)
                require(start <= end, "Reversed citation range")
                numbers.extend(range(start, end + 1))
            else:
                numbers.append(int(bounds[0]))
        for number in numbers:
            require(number in references, f"Missing reference {number}")
            if number not in mapping:
                mapping[number] = len(mapping) + 1
        return "[" + ",".join(str(mapping[number]) for number in numbers) + "]"

    body = re.sub(r"\[(\d+(?:\s*[–-]\s*\d+)?(?:\s*,\s*\d+(?:\s*[–-]\s*\d+)?)*)\]", replace, body)
    bibliography = "\n\n".join(f"[{new}] {references[old]}" for old, new in mapping.items())
    suffix = "\n\n## Figure legends\n" + legends if legends else ""
    return (body.rstrip() + "\n\n## References\n\n" + bibliography + suffix).rstrip() + "\n", mapping


def aligned_pooling_figure(first_seed, second_seed):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.2, 4.5), layout="constrained")
    for group, seed, marker, color, offset in [
            (first_seed, 20261029, "o", "#17627b", .10),
            (second_seed, 20261030, "s", "#b96922", -.10)]:
        metrics = [pair["participant_macro_ap"] for _, pair, _ in group]
        values = [metric["difference_first_minus_second"] for metric in metrics]
        lower = [v - metric["difference_ci95"][0] for v, metric in zip(values, metrics)]
        upper = [metric["difference_ci95"][1] - v for v, metric in zip(values, metrics)]
        positions = [4 - int(fold[-1]) + offset for fold, _, _ in group]
        ax.errorbar(values, positions, xerr=[lower, upper], fmt=marker,
                    capsize=3, color=color, label=f"Seed {seed}", markersize=6)
    ax.axvline(0, color="0.5", lw=.8, linestyle="--")
    ax.set(yticks=range(5), yticklabels=[f"Fold {i}" for i in reversed(range(5))],
           ylim=(-.6, 4.6), xlabel="Graph − time-aligned pooling: participant-macro AP")
    ax.grid(axis="x", alpha=.17)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.legend(frameon=False, fontsize=9)
    for suffix in ("png", "pdf", "svg"):
        fig.savefig(HERE / "figures" / f"aligned_pooling_differences.{suffix}", dpi=240)
    plt.close(fig)


def cohort_flow_figure():
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.2, 6.0), layout="constrained")
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.axis("off")
    items = [(.5, .91, "Loop release roster\n919 participants"),
             (.5, .73, "Source CGM present\n851 participants"),
             (.5, .54, "CGM + basal + bolus + food presence\n835 participants; 56,375,850 eligible windows"),
             (.29, .29, "Development\n652 participants\n44,028,064 windows\n1,296,297 positive labels"),
             (.78, .29, "Reserved performance group\n183 participants\nAggregate eligibility inspected\nNo model performance reported"),
             (.29, .07, "Five disjoint validation groups\n650 AP-defined; 652 Brier participants")]
    for x, y, label in items:
        ax.text(x, y, label, ha="center", va="center", fontsize=9,
                bbox={"boxstyle": "round,pad=.5", "facecolor": "#eef4f6",
                      "edgecolor": "#17627b"})
    for a, b in [((.5, .865), (.5, .78)), ((.5, .685), (.5, .59)),
                 ((.43, .49), (.29, .38)), ((.57, .49), (.78, .38)),
                 ((.29, .20), (.29, .12))]:
        ax.annotate("", xy=b, xytext=a, arrowprops={"arrowstyle": "->", "color": "#44535b"})
    ax.text(.78, .82, "68 without source CGM", fontsize=8, ha="center")
    ax.text(.78, .63, "16 lacking required\nmodality intersection", fontsize=8, ha="center")
    for suffix in ("png", "pdf", "svg"):
        fig.savefig(HERE / "figures" / f"cohort_flow.{suffix}", dpi=240)
    plt.close(fig)


def inline_tokens(value):
    pattern = r"(\*\*.*?\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\))"
    for part in re.split(pattern, value):
        if not part:
            continue
        if part.startswith("**"):
            yield "bold", part[2:-2], None
        elif part.startswith("`"):
            yield "code", part[1:-1], None
        elif re.fullmatch(r"\[[^\]]+\]\([^)]+\)", part):
            match = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", part)
            yield "link", match[1], match[2]
        else:
            yield "text", part, None


def tex_escape(value):
    replacements = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%",
                    "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{",
                    "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
                    "−": "-", "–": "--", "—": "---", "≥": r"$\geq$",
                    "≤": r"$\leq$", "±": r"$\pm$", "×": r"$\times$"}
    return "".join(replacements.get(char, char) for char in value)


def tex_inline(value):
    parts = []
    for kind, content, url in inline_tokens(value):
        content = tex_escape(content)
        # Long source identifiers remain exact in text but may wrap in PDFs.
        content = re.sub(r"\b[0-9a-f]{64}\b", lambda match:
                         r"\allowbreak{}".join(match[0][i:i+8] for i in range(0, 64, 8)), content)
        content = content.replace(r"\_", r"\_\allowbreak{}")
        if kind == "bold":
            content = r"\textbf{" + content + "}"
        elif kind == "code":
            content = r"\texttt{" + content + "}"
        elif kind == "link":
            content = r"\href{" + url.replace("%", r"\%") + "}{" + content + "}"
        parts.append(content)
    return "".join(parts)


def write_tex(document, double_spaced=False):
    output = [r"""\documentclass[11pt,a4paper]{article}
\usepackage[margin=22mm]{geometry}
\usepackage{fontspec}
\setmainfont{Times New Roman}
\setmonofont{Menlo}
\usepackage{graphicx}
\usepackage{longtable}
\usepackage{array}
\usepackage{booktabs}
\usepackage{xcolor}
\usepackage{hyperref}
\hypersetup{colorlinks=true,urlcolor=blue!45!black,linkcolor=black}
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small Temporal event graphs for hypoglycemia prediction}
\fancyhead[R]{\small Working draft}
\fancyfoot[C]{\thepage}
\setlength{\headheight}{14pt}
\setlength{\parindent}{0pt}
\setlength{\parskip}{6pt}
\setlength{\emergencystretch}{3em}
\renewcommand{\arraystretch}{1.2}
\begin{document}
"""]
    if double_spaced:
        output[0] = output[0].replace("\\begin{document}", "\\linespread{1.667}\n\\begin{document}")
    image_caption_pending = False
    table_caption = None
    for kind, value in document:
        if kind == "heading":
            level, title = value
            if double_spaced and (title == "Abstract" or title.startswith("1. Background")):
                output.append("\\clearpage\n")
            if level == 1:
                output.append(r"{\raggedright\hyphenpenalty=10000\LARGE\bfseries " + tex_escape(title) + "\\par}\n\\vspace{8pt}\n")
            else:
                command = "section" if level == 2 else "subsection"
                output.append("\\" + command + "*{" + tex_escape(title) + "}\n")
        elif kind == "paragraph":
            if value.startswith("**Table "):
                table_caption = value
                continue
            output.append(tex_inline(value) + "\n\n")
            if image_caption_pending:
                output.append("\\end{figure}\n")
                image_caption_pending = False
        elif kind == "image":
            output.append(r"\begin{figure}[htbp]\centering\includegraphics[width=.94\linewidth]{" +
                          value[1] + "}\\par\\small\n")
            image_caption_pending = True
        elif kind == "table":
            columns = len(value[0])
            if columns == 2:
                weights = [.25, .75]
            elif columns == 3:
                weights = [.20, .28, .52]
            elif columns == 4:
                weights = [.16, .24, .30, .30]
            elif columns == 5:
                weights = [.07, .12, .12, .345, .345]
            elif columns == 6 and "Graph / pooling AP" in value[0]:
                weights = [.06, .12, .17, .27, .17, .21]
            elif columns == 6:
                weights = [.10, .10, .15, .14, .28, .23]
            elif columns == 8:
                weights = [.04, .12, .08, .08, .22, .08, .08, .30]
            else:
                raise ValueError(f"No LaTeX table layout defined for {columns} columns")
            # Account for 2*tabcolsep for every column so no table exceeds text width.
            specs = "".join(r">{\raggedright\arraybackslash}p{\dimexpr " +
                            f"{weight:.3f}" + r"\linewidth-2\tabcolsep\relax}" for weight in weights)
            output.append("{\\small\n\\setlength{\\tabcolsep}{3pt}\n\\begin{longtable}{" + specs + "}\n\\toprule\n")
            if table_caption:
                output.append(r"\multicolumn{" + str(columns) + r"}{@{}p{\linewidth}@{}}{" +
                              tex_inline(table_caption) + r"} \\*" + "\n\\midrule\n")
                table_caption = None
            output.append(" & ".join(r"\textbf{" + tex_inline(cell) + "}" for cell in value[0]) + r" \\ \midrule" + "\n\\endhead\n")
            for row in value[1:]:
                output.append(" & ".join(tex_inline(cell) for cell in row) + r" \\" + "\n")
            output.append("\\bottomrule\n\\end{longtable}\n}\n")
    output.append("\\end{document}\n")
    (HERE / "manuscript.tex").write_text("".join(output))


def write_docx(document, double_spaced=False):
    w = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    rels = []
    media = {}
    def run(text, bold=False, code=False):
        props = ("<w:b/>" if bold else "") + ('<w:rFonts w:ascii="Courier New" w:hAnsi="Courier New"/>' if code else "")
        return f"<w:r><w:rPr>{props}</w:rPr><w:t xml:space=\"preserve\">{escape(text)}</w:t></w:r>"

    def inline(text):
        content = []
        for kind, value, url in inline_tokens(text):
            if kind == "link":
                rid = f"rId{len(rels)+1}"
                rels.append((rid, "hyperlink", url, True))
                content.append(f'<w:hyperlink r:id="{rid}">{run(value)}</w:hyperlink>')
            else:
                content.append(run(value, kind == "bold", kind == "code"))
        return "".join(content)

    def paragraph(text, style="Normal", page_break=False):
        page = '<w:pageBreakBefore/>' if page_break else ''
        return f'<w:p><w:pPr><w:pStyle w:val="{style}"/>{page}</w:pPr>{inline(text)}</w:p>'

    body = []
    for kind, value in document:
        if kind == "heading":
            level, title = value
            body.append(paragraph(title, "Title" if level == 1 else f"Heading{level-1}",
                                  double_spaced and (title == "Abstract" or title.startswith("1. Background"))))
        elif kind == "paragraph":
            body.append(paragraph(value, "Caption" if value.startswith("**Table ") else "Normal"))
        elif kind == "table":
            cells = len(value[0])
            width_map = {2: [2250, 6750], 3: [1800, 2520, 4680],
                         4: [1440, 2160, 2700, 2700],
                         5: [630, 1080, 1080, 3105, 3105],
                         6: [900, 900, 1350, 1260, 2520, 2070],
                         8: [360, 1080, 720, 720, 1980, 720, 720, 2700]}
            widths = width_map.get(cells, [9000 // cells] * cells)
            table = ['<w:tbl><w:tblPr><w:tblW w:w="9000" w:type="dxa"/>'
                     '<w:tblBorders>' + ''.join(f'<w:{side} w:val="single" w:sz="4" w:color="C9CED4"/>'
                                               for side in ["top", "left", "bottom", "right", "insideH", "insideV"]) +
                     '</w:tblBorders><w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid>' +
                     ''.join(f'<w:gridCol w:w="{width}"/>' for width in widths) + '</w:tblGrid>']
            for i, row in enumerate(value):
                table.append('<w:tr><w:trPr><w:cantSplit/>' + ('<w:tblHeader/>' if i == 0 else '') + '</w:trPr>')
                for width, cell in zip(widths, row):
                    shade = '<w:shd w:fill="EAF0F5"/>' if i == 0 else ''
                    table.append(f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>{shade}</w:tcPr>' +
                                 paragraph(("**" + cell + "**") if i == 0 else cell, "TableText") + '</w:tc>')
                table.append('</w:tr>')
            body.append(''.join(table) + '</w:tbl>' + paragraph(""))
        elif kind == "image":
            path = HERE / value[1]
            name = path.name
            data = path.read_bytes()
            width, height = struct.unpack(">II", data[16:24])
            cx = 5600000
            cy = round(cx * height / width)
            rid = f"rId{len(rels)+1}"
            rels.append((rid, "image", f"media/{name}", False))
            media[f"word/media/{name}"] = data
            body.append(f'''<w:p><w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">
<wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{len(media)}" name="Research figure {len(media)}" descr="{escape(value[0])}"/>
<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
<pic:pic><pic:nvPicPr><pic:cNvPr id="0" name="{name}"/><pic:cNvPicPr/></pic:nvPicPr>
<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>
</a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>''')
    rid = f"rId{len(rels)+1}"
    rels.append((rid, "footer", "footer1.xml", False))
    body.append(f'<w:sectPr><w:footerReference w:type="default" r:id="{rid}"/>'
                '<w:pgSz w:w="11906" w:h="16838"/>'
                '<w:pgMar w:top="1247" w:right="1247" w:bottom="1247" w:left="1247" w:header="500" w:footer="500"/>'
                '</w:sectPr>')
    namespaces = f'xmlns:w="{w}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    namespaces += 'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
    namespaces += 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    namespaces += 'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"'
    doc = f'<w:document {namespaces}><w:body>' + ''.join(body) + '</w:body></w:document>'
    styles = f'''<w:styles xmlns:w="{w}"><w:docDefaults><w:rPrDefault><w:rPr>
<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="22"/>
</w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="276" w:lineRule="auto"/>
</w:pPr></w:pPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>
<w:style w:type="paragraph" w:styleId="Caption"><w:name w:val="Caption"/><w:pPr><w:keepNext/></w:pPr></w:style>
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:pPr><w:keepNext/></w:pPr><w:rPr><w:b/><w:sz w:val="36"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:pPr><w:keepNext/><w:spacing w:before="240" w:after="140"/><w:outlineLvl w:val="0"/></w:pPr><w:rPr><w:b/><w:sz w:val="28"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:pPr><w:keepNext/><w:spacing w:before="180" w:after="100"/><w:outlineLvl w:val="1"/></w:pPr><w:rPr><w:b/><w:sz w:val="24"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="TableText"><w:name w:val="Table Text"/><w:pPr><w:spacing w:after="60" w:line="240"/></w:pPr><w:rPr><w:sz w:val="18"/></w:rPr></w:style>
</w:styles>'''
    if double_spaced:
        styles = styles.replace('w:line="276"', 'w:line="480"')
    rels.append(("rIdStyles", "styles", "styles.xml", False))
    rel_xml = '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    for identity, kind, target, external in rels:
        rel_xml += f'<Relationship Id="{identity}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/{kind}" Target="{escape(target)}"' + (' TargetMode="External"' if external else '') + '/>'
    rel_xml += '</Relationships>'
    content_types = '''<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Default Extension="png" ContentType="image/png"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>
</Types>'''
    footer = f'<w:ftr xmlns:w="{w}"><w:p><w:pPr><w:jc w:val="center"/></w:pPr>' + run("Working draft | ") + '<w:fldSimple w:instr="PAGE"/></w:p></w:ftr>'
    package = {"[Content_Types].xml": content_types, "word/document.xml": doc,
               "word/styles.xml": styles, "word/_rels/document.xml.rels": rel_xml,
               "word/footer1.xml": footer,
               "_rels/.rels": '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>', **media}
    for name, payload in package.items():
        if name.endswith((".xml", ".rels")):
            ET.fromstring(payload)
    with zipfile.ZipFile(HERE / "manuscript.docx", "w", zipfile.ZIP_DEFLATED) as archive:
        for name, payload in package.items():
            archive.writestr(name, payload)
    with zipfile.ZipFile(HERE / "manuscript.docx") as archive:
        require(archive.testzip() is None, "Word package CRC failure")


def main():
    pairs = collect_pairs()
    first = pairs[:5]
    second = pairs[5:]
    cache = read_json("audit/loop_cgm_history_cache_validation.json")
    longer_schedule = read_json("audit/loop_longer_schedule_outer0_seed20261031_graph_vs_aligned_cpu8.json")
    require(sum(p["participants"] for p in first) == cache["participants"] == 652,
            "Development participant reconciliation failed")
    require(sum(p["windows"] for p in first) == cache["windows"] == 44028064,
            "Development window reconciliation failed")
    require(sum(p["positive_labels"] for p in first) == cache["positive_labels"] == 1296297,
            "Positive label reconciliation failed")
    require(sum(p["participant_macro_ap"]["participants"] for p in first) == 650,
            "AP denominator mismatch")
    # Supplementary evidence is fingerprinted; numerical assertions below pin the cited values.
    supplementary = ["audit/loop_temporal_relation_outer0_paired_pilot.json",
                     "audit/loop_graph_vs_capacity_matched_outer0_paired_10000draws_20261019.json",
                     "audit/loop_cgm_canonical_audit.json", "audit/loop_event_instance_cache.json",
                     "audit/loop_window_index_validation.json", "audit/loop_model_split_coverage.json",
                     "audit/loop_cgm_logistic_development_summary_v2.json",
                     "audit/loop_event_vs_cgm_outer0_validation_v3.json",
                     "audit/loop_event_residual_outer0_best_vs_frozen_cgm.json",
                     "audit/loop_full_history_paired_recovered_20261017.json",
                     "audit/loop_full_history_event_zero_ablation_outer0_seed20261003_20261017.json",
                     "audit/loop_full_history_history_event_epoch1_vs_epoch2_strict_20261017.json",
                     "audit/loop_event_sequence_truncation_distribution.json",
                     "audit/loop_multimodal_window_overlap.json", "audit/loop_upload_linkage.json",
                     "audit/loop_mps_graph_sequence_two_seed_five_fold_summary_20261020.json",
                     "audit/loop_relation_typed_vs_generic_seed20261004_five_fold_summary_20261020.json",
                     "audit/loop_relation_endpoint_perturbation_two_seed_five_fold_summary_20261028.json",
                     "audit/loop_event_age_reassignment_two_seed_five_fold_summary_20261029.json",
                     "audit/loop_graph_event_explanation_faithfulness_outer0_seed20261005_20261029_v2.json",
                     "audit/loop_graph_vs_aligned_nongraph_outer0_seed20261029.json",
                     "audit/loop_graph_vs_aligned_nongraph_outer1_seed20261029.json",
                     "audit/loop_graph_vs_aligned_nongraph_outer2_seed20261029_current_source_rerun.json",
                     "audit/loop_graph_vs_aligned_nongraph_outer3_seed20261029_current_source.json",
                     "audit/loop_graph_vs_aligned_nongraph_outer4_seed20261029_source_a4d.json",
                     "audit/novelty_evidence_bundle_20261031_v10.json",
                     "audit/loop_graph_event_ablation_outer0_seed20261031_paired_20261031.json",
                     "audit/loop_graph_vs_aligned_nongraph_seed20261030_five_fold_summary.json",
                     *[f"audit/loop_graph_vs_aligned_nongraph_outer{fold}_seed20261030_source_a4d.json"
                       for fold in range(5)],
                     "audit/loop_graph_vs_aligned_nongraph_two_seed_five_fold_participant_summary.json"]
    supplementary.append("audit/dclp_temporal_coverage_20261031.json")
    supplementary.append("audit/dclp_eligible_windows_20261031.json")
    supplementary.extend([
        "audit/dclp3_frozen_loop_cgm_logistic_transfer_raw_20261031_v3.json",
        "audit/dclp5_frozen_loop_cgm_logistic_transfer_raw_20261031_v3.json",
        "audit/dclp5_frozen_loop_cgm_logistic_transfer_adjusted_20261031_v3.json",
    ])
    for name in supplementary:
        read_json(name)
    dclp_audit = read_json("audit/dclp_temporal_coverage_20261031.json")
    require(dclp_audit.get("identifiers_emitted") is False,
            "DCLP feasibility audit must not emit identifiers")
    dclp_by_name = {row["dataset"]: row for row in dclp_audit["datasets"]}
    require(set(dclp_by_name) == {"dclp3", "dclp5"}
            and dclp_by_name["dclp3"]["cgm"]["parsed_rows"] == 9032235
            and dclp_by_name["dclp3"]["cgm_basal_bolus_participants_with_span_overlap"] == 125
            and dclp_by_name["dclp3"]["basal"]["events_inside_participant_cgm_first_last_span"] == 2607409
            and dclp_by_name["dclp3"]["bolus"]["events_inside_participant_cgm_first_last_span"] == 220424
            and dclp_by_name["dclp5"]["cgm"]["parsed_rows"] == 5536700
            and dclp_by_name["dclp5"]["cgm_basal_bolus_participants_with_span_overlap"] == 100
            and dclp_by_name["dclp5"]["cgm"]["source_order_backward_transitions"] == 287831
            and dclp_by_name["dclp5"]["basal"]["events_inside_participant_cgm_first_last_span"] == 2530007
            and dclp_by_name["dclp5"]["bolus"]["events_inside_participant_cgm_first_last_span"] == 224764,
            "DCLP temporal feasibility totals changed or failed to reconcile")
    dclp_windows = read_json("audit/dclp_eligible_windows_20261031.json")
    require(dclp_windows.get("identifiers_emitted") is False,
            "DCLP window screen must not emit identifiers")
    dclp_window_by_name = {row["dataset"]: row for row in dclp_windows["datasets"]}
    require(set(dclp_window_by_name) == {"dclp3", "dclp5"}
            and dclp_window_by_name["dclp3"]["results"]["eligible_windows"] == 7930123
            and dclp_window_by_name["dclp3"]["results"]["positive_windows"] == 241856
            and dclp_window_by_name["dclp3"]["results"]["participants_with_at_least_one_eligible_window"] == 168
            and dclp_window_by_name["dclp5"]["results"]["eligible_windows"] == 5113177
            and dclp_window_by_name["dclp5"]["results"]["positive_windows"] == 168370
            and dclp_window_by_name["dclp5"]["results"]["participants_with_at_least_one_eligible_window"] == 100
            and dclp_window_by_name["dclp5"]["dclp5_low_sentinel_label_sensitivity"]["eligible_windows_scanned"] == 5118085
            and dclp_window_by_name["dclp5"]["dclp5_low_sentinel_label_sensitivity"]["positive_windows_if_low_indicator_counts_as_hypoglycemia"] == 173297,
            "DCLP eligible-window feasibility totals changed or failed to reconcile")
    dclp_semantics = read_json("audit/dclp_insulin_semantics_20261031.json")
    require(dclp_semantics.get("identifiers_emitted") is False,
            "DCLP insulin-semantics screen must not emit identifiers")
    dclp_semantics_by_name = {row["dataset"]: row for row in dclp_semantics["datasets"]}
    require(set(dclp_semantics_by_name) == {"dclp3", "dclp5"}
            and dclp_semantics_by_name["dclp3"]["basal"]["rows"] == 2610772
            and dclp_semantics_by_name["dclp3"]["basal"]["adjusted_timestamp_differs_from_raw"] == 38382
            and dclp_semantics_by_name["dclp3"]["bolus"]["rows"] == 221292
            and dclp_semantics_by_name["dclp3"]["bolus"]["bolus_type_counts"] == {"Extended": 4257, "Standard": 217035}
            and dclp_semantics_by_name["dclp5"]["basal"]["rows"] == 2531963
            and dclp_semantics_by_name["dclp5"]["basal"]["adjusted_timestamp_differs_from_raw"] == 65190
            and dclp_semantics_by_name["dclp5"]["bolus"]["rows"] == 226685
            and dclp_semantics_by_name["dclp5"]["bolus"]["bolus_type_counts"] == {"Extended": 3169, "Standard": 223516}
            and dclp_semantics_by_name["dclp3"]["basal"]["raw_to_adjusted_naive_delta_seconds"]["absolute_delta_buckets"]["abs_12h_to_24h"] == 25833
            and dclp_semantics_by_name["dclp3"]["basal"]["raw_to_adjusted_naive_delta_seconds"]["absolute_delta_buckets"]["abs_gt_24h"] == 1571
            and dclp_semantics_by_name["dclp5"]["basal"]["raw_to_adjusted_naive_delta_seconds"]["absolute_delta_buckets"]["abs_gt_24h"] == 225
            and "do not establish physical units" in dclp_semantics["limits"][0],
            "DCLP insulin-semantics counts changed or overstate their scope")
    dclp5_raw_policy = read_json("audit/dclp5_eligible_windows_raw_time_20261031.json")
    dclp5_adjusted_policy = read_json("audit/dclp5_eligible_windows_adjusted_time_20261031.json")
    require(dclp5_raw_policy.get("identifiers_emitted") is False
            and dclp5_adjusted_policy.get("identifiers_emitted") is False,
            "DCLP timestamp-policy windows must not emit identifiers")
    raw_policy_row = dclp5_raw_policy["datasets"][0]
    adjusted_policy_row = dclp5_adjusted_policy["datasets"][0]
    require(raw_policy_row["timestamp_policy_pair"] == {
                "cgm": "raw", "events": "raw",
                "note": "These policies select timestamp fields only; they do not resolve timezone, true occurrence, or first availability."}
            and raw_policy_row["results"]["eligible_windows"] == 5113177
            and raw_policy_row["results"]["positive_windows"] == 168370
            and raw_policy_row["results"]["eligible_windows_with_both_event_types_in_lookback"] == 2702133
            and adjusted_policy_row["timestamp_policy_pair"]["cgm"] == "adjusted-preferred"
            and adjusted_policy_row["timestamp_policy_pair"]["events"] == "adjusted-preferred"
            and adjusted_policy_row["results"]["eligible_windows"] == 5123158
            and adjusted_policy_row["results"]["positive_windows"] == 168656
            and adjusted_policy_row["canonicalization"]["conflicting_same_timestamp_groups_removed"] == 5,
            "DCLP5 timestamp-policy window sensitivity changed")
    dclp3_raw_policy = read_json("audit/dclp3_eligible_windows_raw_time_20261031.json")
    require(dclp3_raw_policy.get("identifiers_emitted") is False,
            "DCLP3 raw-time window screen must not emit identifiers")
    dclp3_raw_row = dclp3_raw_policy["datasets"][0]
    require(dclp3_raw_row["timestamp_policy_pair"]["cgm"] == "raw"
            and dclp3_raw_row["timestamp_policy_pair"]["events"] == "raw"
            and dclp3_raw_row["results"]["eligible_windows"] == 7930123
            and dclp3_raw_row["results"]["positive_windows"] == 241856
            and dclp3_raw_row["results"]["eligible_windows_with_both_event_types_in_lookback"] == 2778989,
            "DCLP3 raw-event timestamp sensitivity changed")
    dclp5_span_sensitivity = read_json("audit/dclp_timestamp_policy_sensitivity_20261031.json")
    require(dclp5_span_sensitivity.get("identifiers_emitted") is False,
            "DCLP timestamp-span sensitivity must not emit identifiers")
    span_by_name = {row["dataset"]: row for row in dclp5_span_sensitivity["datasets"]}
    require(span_by_name["dclp3"]["modalities"]["basal"]["adjusted_preferred_only_inside_span"] == 1661
            and span_by_name["dclp5"]["modalities"]["basal"]["raw_only_inside_span"] == 158
            and span_by_name["dclp5"]["modalities"]["basal"]["adjusted_preferred_only_inside_span"] == 2,
            "DCLP raw/adjusted span-overlap sensitivity changed")
    jaeb_transfers = {
        "dclp3_raw": read_json("audit/dclp3_frozen_loop_cgm_logistic_transfer_raw_20261031_v3.json"),
        "dclp5_raw": read_json("audit/dclp5_frozen_loop_cgm_logistic_transfer_raw_20261031_v3.json"),
        "dclp5_adjusted": read_json("audit/dclp5_frozen_loop_cgm_logistic_transfer_adjusted_20261031_v3.json"),
    }
    require(all(result.get("identifiers_emitted") is False
                and result.get("external_dataset_not_in_fit") is True
                and result.get("external_label_use_for_fit_or_recalibration") is False
                and len(result.get("models", [])) == 5
                and set(result["evaluation"]["groups"]) ==
                    {"outer-0", "outer-1", "outer-2", "outer-3", "outer-4", "persistence_slope"}
                for result in jaeb_transfers.values()),
            "Frozen Loop CGM transfer must be aggregate-only, no-refit, and include five folds")
    for result in jaeb_transfers.values():
        groups = result["evaluation"]["groups"]
        baseline = groups["persistence_slope"]
        for fold in range(5):
            model = groups[f"outer-{fold}"]
            require(model["participant_macro_ap"] > baseline["participant_macro_ap"]
                    and model["participant_macro_brier_score"] < baseline["participant_macro_brier_score"],
                    "Frozen Loop CGM pilot direction changed relative to persistence")
    aligned_controls = []
    aligned_specs = [
        ("outer-0", 130, 8885621, 274044,
         "audit/loop_graph_vs_aligned_nongraph_outer0_seed20261029.json",
         (0.4985790754627742, 0.5075203418120227, 0.02053438176333698, 0.020652296550811366)),
        ("outer-1", 141, 9386356, 270499,
         "audit/loop_graph_vs_aligned_nongraph_outer1_seed20261029.json",
         (0.487658202419236, 0.4935604983857929, 0.01948714980996473, 0.019313022438454525)),
        ("outer-2", 124, 8395597, 229814,
         "audit/loop_graph_vs_aligned_nongraph_outer2_seed20261029_current_source_rerun.json",
         (0.4734377438139305, 0.48457794954193395, 0.019138828240460024, 0.018987274373768324)),
        ("outer-3", 130, 9167239, 264561,
         "audit/loop_graph_vs_aligned_nongraph_outer3_seed20261029_current_source.json",
         (0.49840060412490056, 0.5050015127157798, 0.019143067610697537, 0.019064920080476885)),
        ("outer-4", 127, 8193251, 257379,
         "audit/loop_graph_vs_aligned_nongraph_outer4_seed20261029_source_a4d.json",
         (0.5058878305717858, 0.5115789810687427, 0.020477509576533045, 0.020366980839683607)),
    ]
    for fold, participants, windows, positives, path, expected_metrics in aligned_specs:
        aligned = read_json(path)
        require(aligned["comparison_contract"] == "loop-graph-vs-time-aligned-nongraph-v1",
                "Unexpected aligned-control comparison")
        require(aligned["manifest_sha256"] == MANIFEST and
                aligned["window_identity_sha256"] == cache["window_identity_sha256"],
                "Aligned-control cohort identity mismatch")
        require(aligned["seed"] == 20261029 and aligned["group"] == "validation" and
                aligned["participants"] == participants and aligned["windows"] == windows and
                aligned["positive_labels"] == positives and aligned["draws"] == 10000 and
                aligned["identifiers_emitted"] is False,
                f"Aligned-control split or evaluation contract mismatch: {fold}")
        require(aligned["parameter_counts"] == {"aligned_nongraph": 36883, "graph_generic": 36883},
                "Aligned-control parameter mismatch")
        ap, brier = aligned["participant_macro_ap"], aligned["participant_macro_brier"]
        require(all(near(observed, expected) for observed, expected in zip(
                    (ap["first"], ap["second"], brier["first"], brier["second"]), expected_metrics)),
                f"Aligned-control point estimates changed: {fold}")
        run_reports = {}
        for side, variant in (("first", "graph-generic"), ("second", "aligned-nongraph")):
            archive = aligned[f"{side}_archive"]
            run = read_json(f"{archive}/run.json")
            group = run["groups"]["validation"]
            require(run.get("complete") is True and run.get("prediction_identity_verified") is True
                    and run.get("locked_holdout_used") is False,
                    f"Incomplete or holdout-tainted aligned run: {fold}/{variant}")
            require(run.get("fold") == fold and run.get("seed") == 20261029
                    and run.get("epochs") == 2 and run.get("batch_size") == 4096
                    and run.get("workers") == 3 and run.get("variant") == variant
                    and run.get("trainable_parameters") == 36883,
                    f"Aligned run contract mismatch: {fold}/{variant}")
            require(run.get("input_content_sha256") == INPUT_CONTENT
                    and run.get("window_identity_sha256") == aligned["window_identity_sha256"]
                    and group.get("participants") == participants
                    and group.get("windows") == windows
                    and group.get("positive_labels") == positives,
                    f"Aligned run identity mismatch: {fold}/{variant}")
            require(group.get("prediction_window_identity_sha256"),
                    f"Prediction identity missing: {fold}/{variant}")
            run_reports[variant] = run
        graph_run = run_reports["graph-generic"]
        control_run = run_reports["aligned-nongraph"]
        require(graph_run.get("source_sha256") == control_run.get("source_sha256"),
                f"Aligned pair source hashes differ: {fold}")
        require(graph_run.get("training_membership_sha256") == control_run.get("training_membership_sha256"),
                f"Aligned pair training memberships differ: {fold}")
        require(graph_run["groups"]["validation"]["prediction_window_identity_sha256"] ==
                control_run["groups"]["validation"]["prediction_window_identity_sha256"],
                f"Aligned pair prediction identities differ: {fold}")
        aligned_controls.append((fold, aligned, path))
    require(sum(row[1]["participants"] for row in aligned_controls) == 652,
            "Aligned-control folds do not cover the development participants")
    require(sum(row[1]["windows"] for row in aligned_controls) == 44028064,
            "Aligned-control windows do not reconcile")
    aligned_seed2_pairs = []
    seed2_summary = read_json("audit/loop_graph_vs_aligned_nongraph_seed20261030_five_fold_summary.json")
    require(seed2_summary.get("folds") == [f"outer-{i}" for i in range(5)]
            and seed2_summary.get("seed") == 20261030
            and seed2_summary.get("epochs") == 2
            and seed2_summary.get("parameters_per_arm") == 36883
            and seed2_summary.get("locked_holdout_used") is False,
            "Second-seed aggregate contract mismatch")
    require(seed2_summary.get("participants") == 652
            and seed2_summary.get("windows") == 44028064
            and seed2_summary.get("positive_labels") == 1296297,
            "Second-seed aggregate cohort totals do not reconcile")
    require(seed2_summary.get("source_sha256") ==
            "a4d1a91916a675024110e1c30d54546c3aa0d51724480dfdbcdbb141dea71648",
            "Second-seed frozen source digest mismatch")
    for fold, participants, windows, positives in [
            ("outer-0", 130, 8885621, 274044),
            ("outer-1", 141, 9386356, 270499),
            ("outer-2", 124, 8395597, 229814),
            ("outer-3", 130, 9167239, 264561),
            ("outer-4", 127, 8193251, 257379)]:
        path = f"audit/loop_graph_vs_aligned_nongraph_{fold.replace('-', '')}_seed20261030_source_a4d.json"
        paired = read_json(path)
        require(paired.get("comparison_contract") == "loop-graph-vs-time-aligned-nongraph-v1"
                and paired.get("seed") == 20261030
                and paired.get("group") == "validation"
                and paired.get("metric_version") == "threshold-grouped-ap-v2"
                and paired.get("draws") == 10000
                and paired.get("participants") == participants
                and paired.get("windows") == windows
                and paired.get("positive_labels") == positives
                and paired.get("identifiers_emitted") is False,
                f"Second-seed paired audit contract mismatch: {fold}")
        require(paired.get("manifest_sha256") == MANIFEST
                and paired.get("window_identity_sha256") == cache["window_identity_sha256"],
                f"Second-seed cohort identity mismatch: {fold}")
        require(paired.get("parameter_counts") ==
                {"aligned_nongraph": 36883, "graph_generic": 36883},
                f"Second-seed parameter mismatch: {fold}")
        graph_run = read_json(f"{paired['first_archive']}/run.json")
        control_run = read_json(f"{paired['second_archive']}/run.json")
        for run, variant in ((graph_run, "graph-generic"),
                             (control_run, "aligned-nongraph")):
            require(run.get("complete") is True
                    and run.get("prediction_identity_verified") is True
                    and run.get("locked_holdout_used") is False
                    and run.get("fold") == fold
                    and run.get("seed") == 20261030
                    and run.get("epochs") == 2
                    and run.get("trainable_parameters") == 36883
                    and run.get("variant") == variant,
                    f"Second-seed run contract mismatch: {fold}/{variant}")
            require(run.get("source_sha256") == seed2_summary.get("source_sha256")
                    and run.get("manifest_sha256") == MANIFEST
                    and run.get("input_content_sha256") == INPUT_CONTENT,
                    f"Second-seed run provenance mismatch: {fold}/{variant}")
            side = "first" if variant == "graph-generic" else "second"
            run_metrics = run["groups"]["validation"]
            for field in ("participants", "windows", "positive_labels"):
                require(run_metrics.get(field) == paired.get(field),
                        f"Second-seed run count mismatch: {fold}/{variant}/{field}")
            require(near(run_metrics["participant_macro_ap"],
                         paired["participant_macro_ap"][side])
                    and near(run_metrics["participant_macro_brier"],
                             paired["participant_macro_brier"][side])
                    and run_metrics.get("prediction_window_identity_sha256"),
                    f"Second-seed run metric or identity mismatch: {fold}/{variant}")
        require(graph_run.get("source_sha256") == control_run.get("source_sha256")
                and graph_run.get("training_membership_sha256") ==
                    control_run.get("training_membership_sha256")
                and graph_run["groups"]["validation"]["prediction_window_identity_sha256"] ==
                    control_run["groups"]["validation"]["prediction_window_identity_sha256"],
                f"Second-seed pair identity mismatch: {fold}")
        aligned_seed2_pairs.append((fold, paired, path))
    require(sum(row[1]["participants"] for row in aligned_seed2_pairs) == 652
            and sum(row[1]["windows"] for row in aligned_seed2_pairs) == 44028064
            and sum(row[1]["positive_labels"] for row in aligned_seed2_pairs) == 1296297,
            "Second-seed fold totals do not reconcile")
    require(near(seed2_summary["participant_macro_ap_difference"]["graph_minus_control"],
                 -0.01219261726763336)
            and near(seed2_summary["participant_macro_brier_difference"]["graph_minus_control"],
                     0.00017278452889733263),
            "Second-seed aggregate estimate changed")
    two_seed_summary = read_json(
        "audit/loop_graph_vs_aligned_nongraph_two_seed_five_fold_participant_summary.json")
    require(two_seed_summary.get("seeds") == [20261029, 20261030]
            and two_seed_summary.get("folds") == [f"outer-{i}" for i in range(5)]
            and two_seed_summary.get("participants") == 652
            and two_seed_summary.get("ap_defined_participants") == 650
            and two_seed_summary.get("windows") == 44028064
            and two_seed_summary.get("positive_labels") == 1296297
            and two_seed_summary.get("locked_holdout_used") is False,
            "Two-seed participant-summary contract mismatch")
    require(near(two_seed_summary["participant_macro_ap_difference"][
                     "graph_minus_control_after_within_participant_seed_average"],
                 -0.009899666243301021)
            and near(two_seed_summary["participant_macro_brier_difference"][
                         "graph_minus_control_after_within_participant_seed_average"],
                     0.00012643217625050957),
            "Two-seed participant-level aggregate estimate changed")
    require(two_seed_summary["participant_macro_ap_difference"]["control_ahead"] == 639
            and two_seed_summary["participant_macro_ap_difference"]["graph_ahead"] == 11
            and two_seed_summary["participant_macro_brier_difference"]["control_lower_brier"] == 528
            and two_seed_summary["participant_macro_brier_difference"]["graph_lower_brier"] == 124,
            "Two-seed participant-level win counts changed")
    recomputation_receipt = read_json("audit/novelty_recomputation_check_20261031.json")
    require(recomputation_receipt.get("audit_type") ==
            "independent saved-prediction summary recomputation checks"
            and recomputation_receipt.get("date") == SNAPSHOT,
            "Independent summary-recomputation receipt contract mismatch")
    expected_recomputations = {
        "two_seed_participant_summary": (
            "audit/loop_graph_vs_aligned_nongraph_two_seed_five_fold_participant_summary.json",
            "scripts/summarize_two_seed_graph_aligned_control.py"),
        "seed_20261030_five_fold_summary": (
            "audit/loop_graph_vs_aligned_nongraph_seed20261030_five_fold_summary.json",
            "scripts/summarize_graph_aligned_nongraph_folds.py"),
    }
    receipt_by_name = {item.get("name"): item
                       for item in recomputation_receipt.get("checks", [])}
    require(set(receipt_by_name) == set(expected_recomputations),
            "Independent recomputation receipt is missing or has unexpected checks")
    for name, (archive_path, script_path) in expected_recomputations.items():
        item = receipt_by_name[name]
        archived_sha = hashlib.sha256((ROOT / archive_path).read_bytes()).hexdigest()
        script_sha = hashlib.sha256((ROOT / script_path).read_bytes()).hexdigest()
        require(item.get("byte_identical") is True
                and item.get("recomputed_sha256") == item.get("archived_sha256") == archived_sha
                and item.get("recomputation_script") == script_path
                and item.get("recomputation_script_sha256") == script_sha
                and item.get("locked_holdout_used") is False,
                f"Independent summary recomputation did not verify: {name}")
    rejected_graph = read_json("private/pilot_runs/loop_aligned_control_outer4_seed20261029_current_source/graph-generic/run.json")
    rejected_control = read_json("private/pilot_runs/loop_aligned_control_outer4_seed20261029_current_source/aligned-nongraph/run.json")
    require(rejected_graph.get("complete") is True and rejected_control.get("complete") is True
            and rejected_graph.get("source_sha256") != rejected_control.get("source_sha256"),
            "Expected rejected outer-4 source-mismatch artifact not found")
    summary = read_json("audit/loop_mps_graph_sequence_two_seed_five_fold_summary_20261020.json")
    for seed in [20261003, 20261004]:
        seed_pairs = [p for p in pairs if p["training_contract"]["seed"] == seed]
        desc = next(row for row in summary["seed_fold_descriptives"] if row["seed"] == seed)
        require(len(seed_pairs) == 5, f"Incomplete five-fold seed coverage: {seed}")
        require(near(mean(p["participant_macro_ap"]["difference_first_minus_second"] for p in seed_pairs),
                     desc["mean_ap_difference"]), f"Five-fold summary mismatch for seed {seed}")
    split = [(395, 127), (381, 130), (387, 141), (398, 124), (395, 130)]
    table1 = md_table(["Fold", "Train", "Validation / AP-defined", "Internal test", "Validation windows", "Positive labels"],
                      [[i, split[i][0], f"{p['participants']} / {p['participant_macro_ap']['participants']}",
                        split[i][1], f"{p['windows']:,}", f"{p['positive_labels']:,}"] for i, p in enumerate(first)])
    def result_table(group):
        return md_table(["Fold", "Graph AP", "Sequence AP", "AP difference (95% interval)",
                         "Macro-Brier difference (95% interval)"],
                        [[p["training_contract"]["fold"][-1], fmt(p["participant_macro_ap"]["first"]),
                          fmt(p["participant_macro_ap"]["second"]), estimate(p["participant_macro_ap"]),
                          estimate(p["participant_macro_brier"])] for p in group])
    aligned_table = md_table(["Fold", "Participants", "Graph / pooling AP",
                              "AP diff. (95% CI)", "Graph / pooling Brier",
                              "Brier diff. (95% CI)"],
                             [[fold[-1], aligned["participants"],
                               f"{fmt(aligned['participant_macro_ap']['first'])} / {fmt(aligned['participant_macro_ap']['second'])}",
                               estimate(aligned["participant_macro_ap"]),
                               f"{fmt(aligned['participant_macro_brier']['first'])} / {fmt(aligned['participant_macro_brier']['second'])}",
                               estimate(aligned["participant_macro_brier"])]
                              for fold, aligned, _ in aligned_controls])
    aligned_seed2_table = md_table(
        ["Fold", "Participants", "Graph / pooling AP",
         "AP diff. (95% CI)", "Graph / pooling Brier",
         "Brier diff. (95% CI)"],
        [[fold[-1], paired["participants"],
          f"{fmt(paired['participant_macro_ap']['first'])} / {fmt(paired['participant_macro_ap']['second'])}",
          estimate(paired["participant_macro_ap"]),
          f"{fmt(paired['participant_macro_brier']['first'])} / {fmt(paired['participant_macro_brier']['second'])}",
          estimate(paired["participant_macro_brier"])]
         for fold, paired, _ in aligned_seed2_pairs])
    def value_range(values, signed=False):
        return f"{fmt(min(values), signed)} to {fmt(max(values), signed)}"
    replacements = {
        "TABLE1": table1, "TABLE2": result_table(first), "TABLE3": result_table(second),
        "TABLE4": aligned_table, "TABLE5": aligned_seed2_table,
        "AP_RANGE": value_range([p["participant_macro_ap"]["difference_first_minus_second"] for p in first], True),
        "SEED2_AP_RANGE": value_range([p["participant_macro_ap"]["difference_first_minus_second"] for p in second], True),
        "SEED2_MEAN_AP_DIFF": fmt(mean(p["participant_macro_ap"]["difference_first_minus_second"] for p in second), True),
        "MEAN_AP_DIFF": fmt(mean(p["participant_macro_ap"]["difference_first_minus_second"] for p in first), True),
        "MEAN_BRIER_DIFF": fmt(mean(p["participant_macro_brier"]["difference_first_minus_second"] for p in first), True),
        "GRAPH_AP_RANGE": value_range([p["participant_macro_ap"]["first"] for p in first]),
        "SEQ_AP_RANGE": value_range([p["participant_macro_ap"]["second"] for p in first]),
        "FOLD_MEAN_GRAPH_AP": fmt(mean(p["participant_macro_ap"]["first"] for p in first)),
        "FOLD_MEAN_SEQ_AP": fmt(mean(p["participant_macro_ap"]["second"] for p in first)),
        "AP_WINS": str(sum(p["participant_macro_ap"]["positive_difference_participants"] for p in first)),
        "BRIER_WINS": str(sum(p["participant_macro_brier"]["negative_difference_participants"] for p in first)),
        "PREVALENCE": f"{100 * cache['positive_labels'] / cache['windows']:.3f}",
        "LONGER_GRAPH_AP": fmt(longer_schedule["participant_macro_ap"]["first"]),
        "LONGER_CONTROL_AP": fmt(longer_schedule["participant_macro_ap"]["second"]),
        "LONGER_AP_DIFF": fmt(longer_schedule["participant_macro_ap"]["difference_first_minus_second"], True),
        "LONGER_AP_CI": estimate(longer_schedule["participant_macro_ap"]),
        "LONGER_GRAPH_BRIER": fmt(longer_schedule["participant_macro_brier"]["first"]),
        "LONGER_CONTROL_BRIER": fmt(longer_schedule["participant_macro_brier"]["second"]),
        "LONGER_BRIER_DIFF": fmt(longer_schedule["participant_macro_brier"]["difference_first_minus_second"], True),
        "LONGER_BRIER_CI": estimate(longer_schedule["participant_macro_brier"]),
    }
    text = (HERE / "manuscript_template.md").read_text()
    for key, value in replacements.items():
        text = text.replace("{{" + key + "}}", value)
    require("{{" not in text, "Unresolved result placeholder")
    text, citation_mapping = normalize_references(text)
    def word_count(value):
        value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
        return len(re.sub(r"[*`#]", "", value).split())
    abstract = text.split("## Abstract", 1)[1].split("Keywords:", 1)[0]
    main_body = text.split("## 1. Background", 1)[1].split("## References", 1)[0]
    main_paragraphs = " ".join(value for kind, value in blocks(main_body) if kind == "paragraph")
    legends = text.split("## Figure legends", 1)[1]
    journal_counts = {"abstract_with_labels": word_count(abstract),
                      "conservative_main_declarations_legends": word_count(main_paragraphs + " " + legends)}
    text = text.replace("## Abstract", f"Abstract word count: {journal_counts['abstract_with_labels']}. "
                        f"Conservative main-text word count: {journal_counts['conservative_main_declarations_legends']} "
                        "(including declaration and legend prose; excluding tables and references).\n\n## Abstract", 1)
    (HERE / "manuscript.md").write_text(text)
    figures(pairs)
    aligned_pooling_figure(aligned_controls, aligned_seed2_pairs)
    cohort_flow_figure()
    document = list(blocks(text))
    write_tex(document, double_spaced=True)
    write_docx(document, double_spaced=True)
    rows = []
    for p in pairs:
        c, ap, bs = p["training_contract"], p["participant_macro_ap"], p["participant_macro_brier"]
        rows.append({"comparison": "graph_vs_late_fusion_sequence", "training_seed": c["seed"], "bootstrap_seed": p["seed"], "fold": c["fold"],
                     "participants": p["participants"], "ap_defined_participants": ap["participants"],
                     "windows": p["windows"], "positive_labels": p["positive_labels"],
                     "graph_macro_ap": ap["first"], "sequence_macro_ap": ap["second"],
                     "ap_difference": ap["difference_first_minus_second"],
                     "ap_ci_low": ap["difference_ci95"][0], "ap_ci_high": ap["difference_ci95"][1],
                     "graph_macro_brier": bs["first"], "sequence_macro_brier": bs["second"],
                     "brier_difference": bs["difference_first_minus_second"],
                     "brier_ci_low": bs["difference_ci95"][0], "brier_ci_high": bs["difference_ci95"][1],
                     "source": p["manuscript_source"]})
    for fold, aligned, path in aligned_controls:
        aligned_ap = aligned["participant_macro_ap"]
        aligned_brier = aligned["participant_macro_brier"]
        rows.append({"comparison": "graph_vs_time_aligned_nongraph", "training_seed": aligned["seed"],
                     "bootstrap_seed": aligned["seed"], "fold": fold,
                     "participants": aligned["participants"], "ap_defined_participants": aligned_ap["participants"],
                     "windows": aligned["windows"], "positive_labels": aligned["positive_labels"],
                     "graph_macro_ap": aligned_ap["first"], "sequence_macro_ap": aligned_ap["second"],
                     "ap_difference": aligned_ap["difference_first_minus_second"],
                     "ap_ci_low": aligned_ap["difference_ci95"][0], "ap_ci_high": aligned_ap["difference_ci95"][1],
                     "graph_macro_brier": aligned_brier["first"], "sequence_macro_brier": aligned_brier["second"],
                     "brier_difference": aligned_brier["difference_first_minus_second"],
                     "brier_ci_low": aligned_brier["difference_ci95"][0],
                     "brier_ci_high": aligned_brier["difference_ci95"][1],
                     "source": path})
    for fold, aligned, path in aligned_seed2_pairs:
        aligned_ap = aligned["participant_macro_ap"]
        aligned_brier = aligned["participant_macro_brier"]
        rows.append({"comparison": "graph_vs_time_aligned_nongraph",
                     "training_seed": aligned["seed"],
                     "bootstrap_seed": aligned["seed"], "fold": fold,
                     "participants": aligned["participants"],
                     "ap_defined_participants": aligned_ap["participants"],
                     "windows": aligned["windows"],
                     "positive_labels": aligned["positive_labels"],
                     "graph_macro_ap": aligned_ap["first"],
                     "sequence_macro_ap": aligned_ap["second"],
                     "ap_difference": aligned_ap["difference_first_minus_second"],
                     "ap_ci_low": aligned_ap["difference_ci95"][0],
                     "ap_ci_high": aligned_ap["difference_ci95"][1],
                     "graph_macro_brier": aligned_brier["first"],
                     "sequence_macro_brier": aligned_brier["second"],
                     "brier_difference": aligned_brier["difference_first_minus_second"],
                     "brier_ci_low": aligned_brier["difference_ci95"][0],
                     "brier_ci_high": aligned_brier["difference_ci95"][1],
                     "source": path})
    long_ap = longer_schedule["participant_macro_ap"]
    long_brier = longer_schedule["participant_macro_brier"]
    rows.append({"comparison": "graph_vs_time_aligned_nongraph_8_epoch_cpu",
                 "training_seed": longer_schedule["seed"], "bootstrap_seed": longer_schedule["seed"],
                 "fold": "outer-0", "participants": longer_schedule["participants"],
                 "ap_defined_participants": long_ap["participants"],
                 "windows": longer_schedule["windows"], "positive_labels": longer_schedule["positive_labels"],
                 "graph_macro_ap": long_ap["first"], "sequence_macro_ap": long_ap["second"],
                 "ap_difference": long_ap["difference_first_minus_second"],
                 "ap_ci_low": long_ap["difference_ci95"][0], "ap_ci_high": long_ap["difference_ci95"][1],
                 "graph_macro_brier": long_brier["first"], "sequence_macro_brier": long_brier["second"],
                 "brier_difference": long_brier["difference_first_minus_second"],
                 "brier_ci_low": long_brier["difference_ci95"][0], "brier_ci_high": long_brier["difference_ci95"][1],
                 "source": "audit/loop_longer_schedule_outer0_seed20261031_graph_vs_aligned_cpu8.json"})
    with (HERE / "results_snapshot.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    evidence = {"snapshot": SNAPSHOT, "paired_audits": [p["manuscript_source"] for p in pairs] +
                [path for _, _, path in aligned_controls + aligned_seed2_pairs] +
                ["audit/loop_longer_schedule_outer0_seed20261031_graph_vs_aligned_cpu8.json"],
                "sources": sources, "methods_sources": [
                    "src/t1d_tkg/cgm_history_cache.py", "src/t1d_tkg/event_sequence_cache.py",
                    "src/t1d_tkg/temporal_relations.py", "src/t1d_tkg/loop_adapter.py",
                    "kaggle_event_sequence_gru/train_history_controlled.py",
                    "kaggle_event_sequence_gru/train_history_relations.py",
                    "scripts/compare_graph_sequence_archives.py",
                    "scripts/summarize_graph_aligned_nongraph_folds.py",
                    "scripts/summarize_two_seed_graph_aligned_control.py",
                    "scripts/audit_novelty_evidence_bundle.py",
                    "scripts/audit_jaeb_temporal_coverage.py",
                    "scripts/audit_jaeb_eligible_windows.py",
                    "scripts/audit_jaeb_timestamp_policy_sensitivity.py",
                    "scripts/audit_dclp_insulin_semantics.py",
                    "docs/novelty_evidence_audit_correction_2026_10_31.md"],
                "supporting_documents": [
                    "docs/research_master_record_2026_11_08.md",
                    "manuscript/supplementary_methods.md",
                    "manuscript/software_environment.md",
                    "manuscript/submission_readiness_2026_11_08.md",
                    "manuscript/revision_response_2026_11_08.md",
                    "manuscript/reviews/reporting_standards_review_2026_11_08.md",
                    "manuscript/reviews/methods_statistics_review_2026_11_08.md",
                    "manuscript/reviews/clinical_editor_review_2026_11_08.md",
                    "docs/novelty_evidence_report_2026_10_31.md",
                    "docs/primary_source_novelty_check_2026_10_31.md",
                    "docs/primary_source_novelty_update_2026_10_31.md",
                    "docs/targeted_prior_art_search_2026_10_31.md",
                    "docs/literature_search_log.md",
                    "docs/literature_matrix.csv",
                    "docs/loop_extended_schedule_protocol_2026_10_31.md",
                    "docs/dclp_temporal_coverage_audit_2026_10_31.md",
                    "audit/dclp_eligible_windows_20261031.json",
                    "audit/dclp_insulin_semantics_20261031.json",
                    "scripts/audit_dclp_insulin_semantics.py",
                    "audit/dclp5_eligible_windows_raw_time_20261031.json",
                    "audit/dclp5_eligible_windows_adjusted_time_20261031.json",
                    "audit/dclp3_eligible_windows_raw_time_20261031.json",
                    "audit/dclp_timestamp_policy_sensitivity_20261031.json",
                    "scripts/audit_jaeb_timestamp_policy_sensitivity.py",
                    "docs/jaeb_candidate_screening.md"],
                "claim_mapping": {
                    "table_1_cohort_and_supplementary_sequence_results": [p["manuscript_source"] for p in pairs],
                    "tables_2_3_and_figure_2_pooling": [path for _, _, path in aligned_controls + aligned_seed2_pairs],
                    "time_aligned_nongraph_control_seed20261029": [path for _, _, path in aligned_controls],
                    "time_aligned_nongraph_control_seed20261030": [path for _, _, path in aligned_seed2_pairs],
                    "time_aligned_nongraph_control_seed20261030_aggregate":
                        "audit/loop_graph_vs_aligned_nongraph_seed20261030_five_fold_summary.json",
                    "time_aligned_nongraph_control_two_seed_participant_summary":
                        "audit/loop_graph_vs_aligned_nongraph_two_seed_five_fold_participant_summary.json",
                    "longer_schedule_outer0": "audit/loop_longer_schedule_outer0_seed20261031_graph_vs_aligned_cpu8.json",
                    "evidence_bundle_audit": supplementary[25],
                    "dclp_insulin_cgm_span_feasibility": supplementary[-2],
                    "dclp_insulin_only_window_feasibility": supplementary[-1],
                    "dclp_insulin_value_and_timestamp_semantics_screen":
                        "audit/dclp_insulin_semantics_20261031.json",
                    "dclp5_clock_policy_window_sensitivity": [
                        "audit/dclp5_eligible_windows_raw_time_20261031.json",
                        "audit/dclp5_eligible_windows_adjusted_time_20261031.json"],
                    "dclp3_event_clock_window_sensitivity": [
                        "audit/dclp3_eligible_windows_raw_time_20261031.json",
                        "audit/dclp_eligible_windows_20261031.json"],
                    "dclp_raw_adjusted_span_overlap_sensitivity":
                        "audit/dclp_timestamp_policy_sensitivity_20261031.json",
                    "closest_loop_forewarning_prior_art":
                        "docs/primary_source_novelty_update_2026_10_31.md",
                    "independent_saved_prediction_recomputation_receipt":
                        "audit/novelty_recomputation_check_20261031.json",
                    "typed_routing": supplementary[0], "cuda_pair": supplementary[1],
                    "canonicalization": supplementary[2], "event_cache": supplementary[3],
                    "eligibility_index": supplementary[4], "cohort_split": supplementary[5],
                    "historical_logistic": supplementary[6], "event_summary": supplementary[7],
                    "event_residual": supplementary[8], "full_history": supplementary[9],
                    "event_disabled": supplementary[10], "epoch_sensitivity": supplementary[11],
                    "event_truncation": supplementary[12], "event_overlap": supplementary[13],
                    "availability_limits": supplementary[14],
                    "two_seed_five_fold_comparison": supplementary[15],
                    "typed_routing_five_fold": supplementary[16],
                    "endpoint_perturbation": supplementary[17],
                    "event_age_reassignment": supplementary[18],
                    "explanation_sensitivity": supplementary[19]},
                "provenance_limits": [
                    "Top-level paired-audit seed is the bootstrap seed; training seed is training_contract.seed.",
                    "Current method files are inspected implementation references; historic fits have their own source hashes.",
                    "Typed-pilot local raw-prediction recovery not confirmed.",
                    "The manuscript builder uses the aggregate report; the separate five-fold summary script reads saved prediction rows, checks paired identities, and emits no participant identifiers."]}
    for path in evidence["methods_sources"] + evidence["supporting_documents"]:
        data = (ROOT / path).read_bytes()
        evidence["sources"][path] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    evidence["documentation_revision"] = "2026-11-08"
    evidence["template_to_output_reference_numbers"] = citation_mapping
    (HERE / "evidence_map.json").write_text(json.dumps(evidence, indent=2) + "\n")
    verification = {"snapshot": SNAPSHOT, "status": "passed", "paired_comparisons": len(pairs) + len(aligned_controls) + len(aligned_seed2_pairs) + 1,
                    "documentation_revision": "2026-11-08", "journal_format_word_counts": journal_counts,
                    "local_completed_run_summaries_checked": len(pairs) * 2 + len(aligned_controls) * 2 + len(aligned_seed2_pairs) * 2 + 2,
                    "checks": ["training contracts, seeds, optimizer, exact parameter counts",
                               "complete runs, prediction identity, no holdout use in checked summaries",
                               "paired point estimates against local completed run summaries",
                               "paired difference arithmetic and interval ordering",
                               "development participants, AP denominator, window and positive counts",
                    "both five-fold seed summaries agree", "all XML parts parsed and DOCX CRC passed",
                    "all five aligned-control metrics, complete run metadata, matching within-fold sources, and cohort identities match paired audits",
                    "all five second-seed aligned-control pairs match one frozen source digest, strict run metadata, and aggregate prediction-recomputed summary",
                    "independent two-seed and second-seed five-fold recomputations match their archived JSON byte-for-byte and current summarizer script hashes",
                    "five-fold participant aggregate recomputed from saved paired prediction rows and reconciled to all split totals",
                    "two-seed participant-level differences averaged within person after verifying shared fold-level prediction-identity digests",
                               "the initially mismatched outer-4 pair is explicitly rejected and excluded",
                               "the eight-epoch CPU graph/control pair has matching source, training membership, inputs, schedule, parameter count, validation predictions and aggregate metrics",
                               "DCLP3/DCLP5 span and strict-window feasibility totals match identifier-free aggregate audits; these are not model validation",
                               "DCLP pump-value and naive raw-to-adjusted delta summaries match an identifier-free audit; extreme timestamp deltas make eligibility counts conditional, while units, states, availability, and cross-release mappings remain unresolved",
                               "DCLP5 raw/raw and adjusted-preferred/adjusted-preferred window outputs reproduce exact policy-specific eligibility, label, conflict, and lookback totals; these sensitivities do not adjudicate the correct clock",
                               "DCLP3 raw/raw and raw/adjusted-preferred event-clock outputs reproduce exact eligibility, label, and lookback totals; these sensitivities do not adjudicate the correct event clock",
                               "DCLP3/DCLP5 raw-versus-adjusted participant-span overlap changes match an identifier-free audit and are not prediction-window validation",
                               "five frozen Loop CGM-only models transfer without refit to release-local DCLP3/DCLP5 CGM targets and beat persistence; this does not validate event relations or graph models",
                               "template result placeholders resolved"],
                    "aligned_control_source_sha256_by_fold": {fold: read_json(f"{aligned['first_archive']}/run.json")["source_sha256"] for fold, aligned, _ in aligned_controls},
                    "second_seed_source_sha256_by_fold": {fold: read_json(f"{aligned['first_archive']}/run.json")["source_sha256"] for fold, aligned, _ in aligned_seed2_pairs},
                    "two_seed_participant_aggregate": {
                        "ap_difference": two_seed_summary["participant_macro_ap_difference"]["graph_minus_control_after_within_participant_seed_average"],
                        "ap_ci95": two_seed_summary["participant_macro_ap_difference"]["fixed_prediction_participant_bootstrap_95_ci"],
                        "macro_brier_difference": two_seed_summary["participant_macro_brier_difference"]["graph_minus_control_after_within_participant_seed_average"],
                        "macro_brier_ci95": two_seed_summary["participant_macro_brier_difference"]["fixed_prediction_participant_bootstrap_95_ci"],
                    },
                    "independent_summary_recomputations": {
                        name: {key: receipt_by_name[name][key] for key in
                               ("byte_identical", "recomputed_sha256", "recomputation_script_sha256")}
                        for name in sorted(expected_recomputations)},
                    "limits": ["Fold-level bootstrap intervals are reused from paired audits; both five-fold seed aggregate intervals and the two-seed participant aggregate intervals were recomputed by separate summary scripts from saved participant predictions. All intervals condition on fixed fitted models.",
                               "Historical diagnostics fingerprinted; not all historical metrics independently recomputed.",
                               "PDF compilation and visual inspection are separate final checks."]}
    (HERE / "verification.json").write_text(json.dumps(verification, indent=2) + "\n")
    print(json.dumps({"status": "built", "comparisons": len(pairs) + len(aligned_controls) + len(aligned_seed2_pairs) + 1,
                      "words_approx": len(text.split()), "aligned_control_folds": len(aligned_controls) + len(aligned_seed2_pairs), "outputs": ["manuscript.md", "manuscript.docx",
                      "manuscript.tex", "results_snapshot.csv", "evidence_map.json", "verification.json"]}))


if __name__ == "__main__":
    main()
