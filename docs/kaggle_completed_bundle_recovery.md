# Check for the completed Kaggle bundle without retraining

**Resolved on 5 October 2026:** the completed bundle was recovered, its SHA256
verified, and both prediction archives paired. See
`docs/loop_controlled_first_gate_result_2026_10_05.md`. The cell below is
retained only as a recovery record; it does not need to be run again.

When the editor showed the draft session as off, the following check was used
in a **new code cell** in the same private Kaggle notebook without rerunning
the long training cell:

```python
from pathlib import Path
from IPython.display import FileLink, display
import hashlib

bundle = Path('/kaggle/working/loop_controls_20261004T152351Z_f5a83969_bundle.zip')
run = Path('/kaggle/working/loop_controls_20261004T152351Z_f5a83969')
print('bundle exists:', bundle.is_file(), 'run directory exists:', run.is_dir())
if bundle.is_file():
    assert bundle.stat().st_size == 245220538
    with bundle.open('rb') as handle:
        digest = hashlib.file_digest(handle, 'sha256').hexdigest()
    assert digest == '100f046deabaf733d2bc27f8ae1537dcc88f892da9d2a1f4d489544b03aa61bd'
    print('bundle checksum verified:', digest)
    display(FileLink(str(bundle)))
else:
    print('run contents:', [p.name for p in run.iterdir()] if run.is_dir() else [])
```

If the bundle exists, download the new link and keep it private. If only the
run directory exists, preserve its `result.json`, checkpoint and `predictions`
files before another session reset. If neither exists, the notebook's visible
metrics remain a provisional result; the two-model first gate needs to be
rerun with an output-preservation method tested before the long fit.
