# SPEC CPU 2017 Benchmarking

Compiler comparison (GCC, Clang, ICC) of SPEC CPU 2017 integer-rate benchmarks across 32/64-bit and `-O0`–`-O3`.

## Layout

| Path | Contents |
| --- | --- |
| `report.pdf` | Final report |
| `clang_results.tar.gz`, `gcc_results.tar.gz`, `icc_results.tar.gz` | Zipped SPEC run outputs for each compiler |
| `extracted_results/` | Unpacked copies of those archives |
| `results/` | Final compiled CSV/JSON (`result.csv`, `result.json`) |
| `plots/` | Runtime and SPECrate plots |
| `scripts/` | `parse_results.py` and `plot_results.py` |

```text
SPEC-CPU2017-Benchmarking/
├── report.pdf
├── clang_results.tar.gz
├── gcc_results.tar.gz
├── icc_results.tar.gz
├── extracted_results/
│   ├── clang/
│   ├── gcc/
│   └── icc/
├── results/
│   ├── result.csv
│   └── result.json
├── plots/
└── scripts/
    ├── parse_results.py
    └── plot_results.py
```

To regenerate the compiled results and plots from `extracted_results/`:

```bash
python3 scripts/parse_results.py
python3 scripts/plot_results.py
```
