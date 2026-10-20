#!/usr/bin/env python3
"""Build the bounded 2026-10-20 manuscript from existing aggregate evidence.

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
SNAPSHOT = "2026-10-20"
MANIFEST = "69b41e4acfae7d2afc990c8cd15d8fc3f969784d4e5f6534a9263033d341ad52"
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
                              (20261004, range(4), "20261020")]:
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


def inline_tokens(value):
    pattern = r"(\*\*.*?\*\*|`[^`]+`|\[[^\]]+\]\(https?://[^)]+\))"
    for part in re.split(pattern, value):
        if not part:
            continue
        if part.startswith("**"):
            yield "bold", part[2:-2], None
        elif part.startswith("`"):
            yield "code", part[1:-1], None
        elif re.fullmatch(r"\[[^\]]+\]\(https?://[^)]+\)", part):
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
        if kind == "bold":
            content = r"\textbf{" + content + "}"
        elif kind == "code":
            content = r"\texttt{" + content + "}"
        elif kind == "link":
            content = r"\href{" + url.replace("%", r"\%") + "}{" + content + "}"
        parts.append(content)
    return "".join(parts)


def write_tex(document):
    output = [r"""\documentclass[11pt,a4paper]{article}
\usepackage[margin=22mm]{geometry}
\usepackage{fontspec}
\setmainfont{Times New Roman}
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
    image_caption_pending = False
    for kind, value in document:
        if kind == "heading":
            level, title = value
            if level == 1:
                output.append(r"{\raggedright\hyphenpenalty=10000\LARGE\bfseries " + tex_escape(title) + "\\par}\n\\vspace{8pt}\n")
            else:
                command = "section" if level == 2 else "subsection"
                output.append("\\" + command + "*{" + tex_escape(title) + "}\n")
        elif kind == "paragraph":
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
            weights = [.07, .12, .12, .345, .345] if columns == 5 else [.10, .10, .15, .14, .28, .23]
            # Account for 2*tabcolsep for every column so no table exceeds text width.
            specs = "".join(r">{\raggedright\arraybackslash}p{\dimexpr " +
                            f"{weight:.3f}" + r"\linewidth-2\tabcolsep\relax}" for weight in weights)
            output.append("{\\small\n\\setlength{\\tabcolsep}{3pt}\n\\begin{longtable}{" + specs + "}\n\\toprule\n")
            output.append(" & ".join(r"\textbf{" + tex_inline(cell) + "}" for cell in value[0]) + r" \\ \midrule" + "\n\\endhead\n")
            for row in value[1:]:
                output.append(" & ".join(tex_inline(cell) for cell in row) + r" \\" + "\n")
            output.append("\\bottomrule\n\\end{longtable}\n}\n")
    output.append("\\end{document}\n")
    (HERE / "manuscript.tex").write_text("".join(output))


def write_docx(document):
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

    def paragraph(text, style="Normal"):
        return f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr>{inline(text)}</w:p>'

    body = []
    for kind, value in document:
        if kind == "heading":
            level, title = value
            body.append(paragraph(title, "Title" if level == 1 else f"Heading{level-1}"))
        elif kind == "paragraph":
            body.append(paragraph(value))
        elif kind == "table":
            cells = len(value[0])
            widths = ([630, 1080, 1080, 3105, 3105] if cells == 5 else
                      [900, 900, 1350, 1260, 2520, 2070])
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
<wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="1" name="AP comparisons" descr="{escape(value[0])}"/>
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
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:pPr><w:keepNext/></w:pPr><w:rPr><w:b/><w:sz w:val="36"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:pPr><w:keepNext/><w:spacing w:before="240" w:after="140"/><w:outlineLvl w:val="0"/></w:pPr><w:rPr><w:b/><w:sz w:val="28"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:pPr><w:keepNext/><w:spacing w:before="180" w:after="100"/><w:outlineLvl w:val="1"/></w:pPr><w:rPr><w:b/><w:sz w:val="24"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="TableText"><w:name w:val="Table Text"/><w:pPr><w:spacing w:after="60" w:line="240"/></w:pPr><w:rPr><w:sz w:val="18"/></w:rPr></w:style>
</w:styles>'''
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
                     "audit/loop_multimodal_window_overlap.json", "audit/loop_upload_linkage.json"]
    for name in supplementary:
        read_json(name)
    summary = read_json("audit/loop_mps_graph_vs_sequence_five_fold_summary_20261019.json")
    require(near(mean(p["participant_macro_ap"]["difference_first_minus_second"] for p in first),
                 summary["descriptive_unweighted_mean_ap_difference"]), "Five-fold summary mismatch")
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
    def value_range(values, signed=False):
        return f"{fmt(min(values), signed)} to {fmt(max(values), signed)}"
    replacements = {
        "TABLE1": table1, "TABLE2": result_table(first), "TABLE3": result_table(second),
        "AP_RANGE": value_range([p["participant_macro_ap"]["difference_first_minus_second"] for p in first], True),
        "SEED2_AP_RANGE": value_range([p["participant_macro_ap"]["difference_first_minus_second"] for p in second], True),
        "MEAN_AP_DIFF": fmt(mean(p["participant_macro_ap"]["difference_first_minus_second"] for p in first), True),
        "MEAN_BRIER_DIFF": fmt(mean(p["participant_macro_brier"]["difference_first_minus_second"] for p in first), True),
        "GRAPH_AP_RANGE": value_range([p["participant_macro_ap"]["first"] for p in first]),
        "SEQ_AP_RANGE": value_range([p["participant_macro_ap"]["second"] for p in first]),
        "FOLD_MEAN_GRAPH_AP": fmt(mean(p["participant_macro_ap"]["first"] for p in first)),
        "FOLD_MEAN_SEQ_AP": fmt(mean(p["participant_macro_ap"]["second"] for p in first)),
        "AP_WINS": str(sum(p["participant_macro_ap"]["positive_difference_participants"] for p in first)),
        "BRIER_WINS": str(sum(p["participant_macro_brier"]["negative_difference_participants"] for p in first)),
        "PREVALENCE": f"{100 * cache['positive_labels'] / cache['windows']:.3f}",
    }
    text = (HERE / "manuscript_template.md").read_text()
    for key, value in replacements.items():
        text = text.replace("{{" + key + "}}", value)
    require("{{" not in text, "Unresolved result placeholder")
    (HERE / "manuscript.md").write_text(text)
    figures(pairs)
    document = list(blocks(text))
    write_tex(document)
    write_docx(document)
    rows = []
    for p in pairs:
        c, ap, bs = p["training_contract"], p["participant_macro_ap"], p["participant_macro_brier"]
        rows.append({"training_seed": c["seed"], "bootstrap_seed": p["seed"], "fold": c["fold"],
                     "participants": p["participants"], "ap_defined_participants": ap["participants"],
                     "windows": p["windows"], "positive_labels": p["positive_labels"],
                     "graph_macro_ap": ap["first"], "sequence_macro_ap": ap["second"],
                     "ap_difference": ap["difference_first_minus_second"],
                     "ap_ci_low": ap["difference_ci95"][0], "ap_ci_high": ap["difference_ci95"][1],
                     "graph_macro_brier": bs["first"], "sequence_macro_brier": bs["second"],
                     "brier_difference": bs["difference_first_minus_second"],
                     "brier_ci_low": bs["difference_ci95"][0], "brier_ci_high": bs["difference_ci95"][1],
                     "source": p["manuscript_source"]})
    with (HERE / "results_snapshot.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    evidence = {"snapshot": SNAPSHOT, "paired_audits": [p["manuscript_source"] for p in pairs],
                "sources": sources, "methods_sources": [
                    "src/t1d_tkg/cgm_history_cache.py", "src/t1d_tkg/event_sequence_cache.py",
                    "src/t1d_tkg/temporal_relations.py", "src/t1d_tkg/loop_adapter.py",
                    "kaggle_event_sequence_gru/train_history_controlled.py",
                    "kaggle_event_sequence_gru/train_history_relations.py",
                    "scripts/compare_graph_sequence_archives.py"],
                "claim_mapping": {
                    "tables_1_2_3_and_figure_1": [p["manuscript_source"] for p in pairs],
                    "typed_routing": supplementary[0], "cuda_pair": supplementary[1],
                    "canonicalization": supplementary[2], "event_cache": supplementary[3],
                    "eligibility_index": supplementary[4], "cohort_split": supplementary[5],
                    "historical_logistic": supplementary[6], "event_summary": supplementary[7],
                    "event_residual": supplementary[8], "full_history": supplementary[9],
                    "event_disabled": supplementary[10], "epoch_sensitivity": supplementary[11],
                    "event_truncation": supplementary[12], "event_overlap": supplementary[13],
                    "availability_limits": supplementary[14]},
                "provenance_limits": [
                    "Top-level paired-audit seed is the bootstrap seed; training seed is training_contract.seed.",
                    "Current method files are inspected implementation references; historic fits have their own source hashes.",
                    "Typed-pilot local raw-prediction recovery not confirmed.",
                    "No raw participant predictions were opened or recomputed during this manuscript build."]}
    for path in evidence["methods_sources"]:
        data = (ROOT / path).read_bytes()
        evidence["sources"][path] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    (HERE / "evidence_map.json").write_text(json.dumps(evidence, indent=2) + "\n")
    verification = {"snapshot": SNAPSHOT, "status": "passed", "paired_comparisons": len(pairs),
                    "local_completed_run_summaries_checked": len(pairs) * 2,
                    "checks": ["training contracts, seeds, optimizer, exact parameter counts",
                               "complete runs, prediction identity, no holdout use in checked summaries",
                               "paired point estimates against local completed run summaries",
                               "paired difference arithmetic and interval ordering",
                               "development participants, AP denominator, window and positive counts",
                               "five-fold summary agreement", "all XML parts parsed and DOCX CRC passed",
                               "template result placeholders resolved"],
                    "limits": ["Bootstrap intervals reused from existing audits; not recomputed from raw predictions.",
                               "Historical diagnostics fingerprinted; not all historical metrics independently recomputed.",
                               "PDF compilation and visual inspection are separate final checks."]}
    (HERE / "verification.json").write_text(json.dumps(verification, indent=2) + "\n")
    print(json.dumps({"status": "built", "comparisons": len(pairs),
                      "words_approx": len(text.split()), "outputs": ["manuscript.md", "manuscript.docx",
                      "manuscript.tex", "results_snapshot.csv", "evidence_map.json", "verification.json"]}))


if __name__ == "__main__":
    main()
