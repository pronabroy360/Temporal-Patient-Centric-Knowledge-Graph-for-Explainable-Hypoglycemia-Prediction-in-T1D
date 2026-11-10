# Recorded software environments and reconstruction limits


Prepared 8 November 2026. Historical training versions below are transcribed from completed-run metadata for the 21 central paired comparisons. They are not inferred from the current documentation interpreter or asserted to be a full environment lock. No participant rows or predictions were read for this summary.


| Comparison / seed | Matched pairs | Device | Recorded versions |
|---|---:|---|---|

| graph vs late fusion sequence / 20261003 | 5 | mps | Python 3.12.13; NumPy 2.5.4; PyTorch 2.14.1 |

| graph vs late fusion sequence / 20261004 | 5 | mps | Python 3.12.13; NumPy 2.5.4; PyTorch 2.14.1 |

| graph vs time aligned nongraph / 20261029 | 5 | mps | Python 3.12.13; NumPy 2.5.4; PyTorch 2.15.0 |

| graph vs time aligned nongraph / 20261030 | 5 | mps | Python 3.12.13; NumPy 2.5.4; PyTorch 2.15.0 |

| graph vs time aligned nongraph 8 epoch cpu / 20261031 | 1 | cpu | Python 3.12.13; NumPy 2.5.4; PyTorch 2.15.0 |


Both sides of each accepted pair have identical recorded environment fields in this table. The first pooling seed uses different whole-project source hashes across folds; matching Python/library fields does not establish identical code. MPS/CPU execution is not bitwise reproduction of CUDA. Historical CUDA/typed-pilot and earlier logistic runs require their own retained run metadata; this table does not invent a complete environment for those earlier analyses.


## Current documentation build


Interpreter: Python 3.14.4, Darwin arm64.

numpy: 2.4.3.

matplotlib: 3.10.8.


The build uses the Python standard library for Office Open XML and ZIP/JSON generation, Matplotlib/NumPy for figures, cached Tectonic for XeLaTeX/PDF, Times New Roman/Menlo fonts on the current Mac, and Poppler pdfinfo/pdftotext/pdftoppm for document checks. The main DOCX specifies double line spacing; the PDF uses native LaTeX linespread 1.667 to avoid an unavailable setspace package. The supplement/master exports use compact line spacing for reference use.


## Reconstruction requirements

A public reproducibility release still needs an immutable code revision, code license, retained platform-specific dependency specifications and explicit data-access terms. A clean raw-to-cache rebuild also requires reacquiring the two missing basal source tables. This documentation environment is separate from training environments; current code and package versions must not silently substitute for a historical run. Exact deterministic behavior can vary by backend. The [evidence map](evidence_map.json), [full numerical snapshot](results_snapshot.csv) and [submission register](submission_readiness_2026_11_08.md) preserve the related scope.
