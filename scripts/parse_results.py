#!/usr/bin/env python3
"""
parse_results.py - SPEC CPU 2017 Benchmark Results Parser

Extracts benchmark runtimes and SPECrate scores from extracted results.
Supports GCC, Clang, and ICC across 32-bit and 64-bit builds with -O0, -O1, -O2, -O3 optimizations.

Outputs structured CSV and JSON files in results/ as result.csv / result.json.
"""

import os
import csv
import json

# Mapping of file numbers to configuration metadata
RUN_MAPPING = {
    'gcc': {
        '003': ('GCC', '32-bit', '-O0'),
        '004': ('GCC', '64-bit', '-O0'),
        '007': ('GCC', '32-bit', '-O1'),
        '008': ('GCC', '64-bit', '-O1'),
        '009': ('GCC', '32-bit', '-O2'),
        '010': ('GCC', '64-bit', '-O2'),
        '011': ('GCC', '32-bit', '-O3'),
        '012': ('GCC', '64-bit', '-O3'),
    },
    'clang': {
        '020': ('Clang', '32-bit', '-O0'),
        '021': ('Clang', '64-bit', '-O0'),
        '022': ('Clang', '32-bit', '-O1'),
        '023': ('Clang', '64-bit', '-O1'),
        '024': ('Clang', '32-bit', '-O2'),
        '025': ('Clang', '64-bit', '-O2'),
        '026': ('Clang', '32-bit', '-O3'),
        '027': ('Clang', '64-bit', '-O3'),
    },
    'icc': {
        '029': ('ICC', '32-bit', '-O0'),
        '030': ('ICC', '64-bit', '-O0'),
        '031': ('ICC', '32-bit', '-O1'),
        '032': ('ICC', '64-bit', '-O1'),
        '033': ('ICC', '32-bit', '-O2'),
        '034': ('ICC', '64-bit', '-O2'),
        '035': ('ICC', '32-bit', '-O3'),
        '036': ('ICC', '64-bit', '-O3'),
    }
}

BENCHMARK_NAMES = [
    '500.perlbench_r',
    '502.gcc_r',
    '505.mcf_r',
    '520.omnetpp_r',
    '523.xalancbmk_r',
    '525.x264_r',
    '531.deepsjeng_r',
    '541.leela_r',
    '557.xz_r'
]


def parse_all_results(base_dir='extracted_results'):
    records = []

    for comp, file_map in RUN_MAPPING.items():
        for run_num, (compiler_name, bitness, opt_level) in file_map.items():
            csv_path = os.path.join(base_dir, comp, 'result', f'CPU2017.{run_num}.intrate.refrate.csv')
            if not os.path.exists(csv_path):
                print(f"[Warning] File not found: {csv_path}")
                continue

            with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.reader(f)
                in_selected_section = False

                for row in reader:
                    if not row:
                        continue
                    if row[0] == 'Selected Results Table':
                        in_selected_section = True
                        continue
                    if in_selected_section and (row[0].startswith('SPECrate2017') or row[0].startswith('runcpu command') or row[0].startswith(' ')):
                        in_selected_section = False
                        continue

                    if in_selected_section and len(row) >= 4 and row[0] in BENCHMARK_NAMES:
                        bm_name = row[0]
                        try:
                            runtime_sec = float(row[2])
                            spec_rate = float(row[3])

                            records.append({
                                'benchmark': bm_name,
                                'compiler': compiler_name,
                                'bitness': bitness,
                                'optimization': opt_level,
                                'runtime_seconds': runtime_sec,
                                'spec_rate': spec_rate,
                                'run_id': run_num,
                                'suite': comp
                            })
                        except ValueError:
                            print(f"[Error] Could not parse floats for {bm_name} in {csv_path}: {row}")

    return records


def save_results(records, output_dir='results'):
    os.makedirs(output_dir, exist_ok=True)

    csv_file = os.path.join(output_dir, 'result.csv')
    fieldnames = ['benchmark', 'compiler', 'bitness', 'optimization', 'runtime_seconds',
                  'spec_rate', 'run_id', 'suite']
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"Saved {len(records)} records to {csv_file}")

    json_file = os.path.join(output_dir, 'result.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2)
    print(f"Saved JSON data to {json_file}")


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, '..'))
    extracted_dir = os.path.join(root_dir, 'extracted_results')
    results_dir = os.path.join(root_dir, 'results')

    data = parse_all_results(extracted_dir)
    save_results(data, results_dir)
