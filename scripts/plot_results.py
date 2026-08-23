#!/usr/bin/env python3
"""
plot_results.py - SPEC CPU 2017 Benchmark Visualization Generator

Generates high-resolution, publication-quality plots for SPEC CPU 2017 Integer Rate benchmarks:
1. 9 Individual Benchmark Plots (Runtime vs Opt Level & Score vs Opt Level for GCC/Clang/ICC 32/64-bit)
2. 3x3 Summary Grid Plot of all benchmarks
3. Compiler Speedup & Bitness Analysis Plots
"""

import os
import csv
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt

# Set aesthetic plot style
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#CCCCCC'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#EBEBEB'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7

# Benchmark metadata descriptions
BENCHMARK_TITLES = {
    '500.perlbench_r': '500.perlbench_r (Perl Interpreter)',
    '502.gcc_r': '502.gcc_r (C Compiler)',
    '505.mcf_r': '505.mcf_r (Combinatorial Optimization / Network Flow)',
    '520.omnetpp_r': '520.omnetpp_r (Discrete Event Simulation)',
    '523.xalancbmk_r': '523.xalancbmk_r (XML / XSLT Processing)',
    '525.x264_r': '525.x264_r (H.264 / AVC Video Encoder)',
    '531.deepsjeng_r': '531.deepsjeng_r (Chess Algorithm Search Engine)',
    '541.leela_r': '541.leela_r (Go Game AI)',
    '557.xz_r': '557.xz_r (Data Compression)'
}

# Configuration styling (Colors, Markers, Linestyles)
SERIES_STYLES = {
    ('GCC', '32-bit'): {'color': '#1f77b4', 'linestyle': '-', 'marker': 'o', 'label': 'GCC (32-bit)'},
    ('GCC', '64-bit'): {'color': '#1f77b4', 'linestyle': '--', 'marker': 's', 'label': 'GCC (64-bit)'},
    ('Clang', '32-bit'): {'color': '#2ca02c', 'linestyle': '-', 'marker': '^', 'label': 'Clang (32-bit)'},
    ('Clang', '64-bit'): {'color': '#2ca02c', 'linestyle': '--', 'marker': 'D', 'label': 'Clang (64-bit)'},
    ('ICC', '32-bit'): {'color': '#d62728', 'linestyle': '-', 'marker': 'v', 'label': 'ICC (32-bit)'},
    ('ICC', '64-bit'): {'color': '#d62728', 'linestyle': '--', 'marker': 'P', 'label': 'ICC (64-bit)'},
}

OPT_LEVELS = ['-O0', '-O1', '-O2', '-O3']

def load_data(csv_path):
    data = defaultdict(lambda: defaultdict(dict))
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            bm = row['benchmark']
            comp = row['compiler']
            bitness = row['bitness']
            opt = row['optimization']
            runtime = float(row['runtime_seconds'])
            score = float(row['spec_rate'])
            
            data[bm][(comp, bitness)][opt] = {
                'runtime': runtime,
                'score': score
            }
    return data

def plot_individual_benchmark(bm_name, bm_data, output_dir):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 9), sharex=True, gridspec_kw={'hspace': 0.15})
    
    title = BENCHMARK_TITLES.get(bm_name, bm_name)
    fig.suptitle(f'SPEC CPU 2017 Benchmark: {title}', fontsize=14, fontweight='bold', y=0.98)
    
    # Plot curves
    for (comp, bitness), style in SERIES_STYLES.items():
        if (comp, bitness) not in bm_data:
            continue
        
        opt_dict = bm_data[(comp, bitness)]
        runtimes = [opt_dict[opt]['runtime'] for opt in OPT_LEVELS if opt in opt_dict]
        scores = [opt_dict[opt]['score'] for opt in OPT_LEVELS if opt in opt_dict]
        x_opts = [opt for opt in OPT_LEVELS if opt in opt_dict]
        
        # Subplot 1: Runtime (Seconds)
        ax1.plot(
            x_opts, runtimes,
            color=style['color'],
            linestyle=style['linestyle'],
            marker=style['marker'],
            markersize=7,
            linewidth=2,
            label=style['label']
        )
        
        # Subplot 2: SPECrate Score
        ax2.plot(
            x_opts, scores,
            color=style['color'],
            linestyle=style['linestyle'],
            marker=style['marker'],
            markersize=7,
            linewidth=2,
            label=style['label']
        )
    
    # Subplot 1 formatting
    ax1.set_ylabel('Execution Time (seconds)\n[Lower is Better]', fontsize=11, fontweight='semibold')
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.legend(loc='upper right', frameon=True, facecolor='#F8F9FA', edgecolor='#E0E0E0', fontsize=9.5, ncol=2)
    ax1.set_title('Runtime vs. Optimization Level', fontsize=11, pad=8)
    
    # Annotate min/max runtimes on ax1
    for (comp, bitness), style in SERIES_STYLES.items():
        if (comp, bitness) in bm_data:
            opt_dict = bm_data[(comp, bitness)]
            if '-O0' in opt_dict and '-O3' in opt_dict:
                o0_rt = opt_dict['-O0']['runtime']
                o3_rt = opt_dict['-O3']['runtime']
                speedup = o0_rt / o3_rt if o3_rt > 0 else 1.0
                # print summary info
    
    # Subplot 2 formatting
    ax2.set_xlabel('Optimization Level', fontsize=11, fontweight='semibold')
    ax2.set_ylabel('SPECrate2017_int Base Score\n[Higher is Better]', fontsize=11, fontweight='semibold')
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.set_title('SPECrate Score vs. Optimization Level', fontsize=11, pad=8)
    
    # Safe filename
    clean_name = bm_name.replace('.', '_')
    out_file = os.path.join(output_dir, f'{clean_name}.png')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(out_file, dpi=300)
    plt.close()
    print(f"Generated plot: {out_file}")

def plot_summary_grid(data, output_dir):
    fig, axes = plt.subplots(3, 3, figsize=(16, 14), sharex=True)
    fig.suptitle('SPEC CPU 2017 Integer Rate Benchmarks: Execution Time vs. Optimization Level', fontsize=16, fontweight='bold', y=0.99)
    
    bm_list = sorted(data.keys())
    
    for idx, bm_name in enumerate(bm_list):
        ax = axes[idx // 3, idx % 3]
        bm_data = data[bm_name]
        
        for (comp, bitness), style in SERIES_STYLES.items():
            if (comp, bitness) not in bm_data:
                continue
            opt_dict = bm_data[(comp, bitness)]
            runtimes = [opt_dict[opt]['runtime'] for opt in OPT_LEVELS if opt in opt_dict]
            x_opts = [opt for opt in OPT_LEVELS if opt in opt_dict]
            
            ax.plot(
                x_opts, runtimes,
                color=style['color'],
                linestyle=style['linestyle'],
                marker=style['marker'],
                markersize=5,
                linewidth=1.8,
                label=style['label']
            )
            
        short_name = bm_name.split('.')[1] if '.' in bm_name else bm_name
        ax.set_title(f'{short_name}', fontsize=12, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.6)
        if idx % 3 == 0:
            ax.set_ylabel('Runtime (s)', fontsize=10)
        if idx // 3 == 2:
            ax.set_xlabel('Optimization Level', fontsize=10)
            
    # Add shared legend at bottom
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, 0.01), ncol=6, frameon=True, facecolor='#F8F9FA', fontsize=10)
    
    plt.subplots_adjust(bottom=0.08, top=0.94, hspace=0.25, wspace=0.25)
    out_file = os.path.join(output_dir, '00_summary_grid_runtime.png')
    plt.savefig(out_file, dpi=300)
    plt.close()
    print(f"Generated summary grid plot: {out_file}")

def plot_bitness_comparison(data, output_dir):
    """
    Plots the average 64-bit speedup over 32-bit ((Runtime_32 - Runtime_64)/Runtime_32 * 100%)
    per compiler across optimization levels.
    """
    compilers = ['GCC', 'Clang', 'ICC']
    opts = OPT_LEVELS
    
    speedups = defaultdict(lambda: defaultdict(list))
    
    for bm_name, bm_data in data.items():
        for comp in compilers:
            for opt in opts:
                if (comp, '32-bit') in bm_data and (comp, '64-bit') in bm_data:
                    t32 = bm_data[(comp, '32-bit')].get(opt, {}).get('runtime')
                    t64 = bm_data[(comp, '64-bit')].get(opt, {}).get('runtime')
                    if t32 and t64 and t32 > 0:
                        pct_speedup = (t32 - t64) / t32 * 100.0
                        speedups[comp][opt].append(pct_speedup)
                        
    fig, ax = plt.subplots(figsize=(9, 6))
    
    bar_width = 0.25
    x = np.arange(len(opts))
    
    colors = {'GCC': '#1f77b4', 'Clang': '#2ca02c', 'ICC': '#d62728'}
    
    for i, comp in enumerate(compilers):
        means = [np.mean(speedups[comp][opt]) for opt in opts]
        rects = ax.bar(x + i*bar_width, means, bar_width, label=comp, color=colors[comp], alpha=0.85, edgecolor='black', linewidth=0.5)
        
        # Add value labels
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:+.1f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3 if height >= 0 else -10),
                        textcoords="offset points",
                        ha='center', va='bottom' if height >= 0 else 'top',
                        fontsize=8.5, fontweight='bold')

    ax.axhline(0, color='black', linewidth=0.8)
    ax.set_ylabel('Mean 64-bit Speedup over 32-bit (%)', fontsize=11, fontweight='bold')
    ax.set_xlabel('Optimization Level', fontsize=11, fontweight='bold')
    ax.set_title('64-bit vs 32-bit Performance Advantage by Compiler', fontsize=13, fontweight='bold', pad=12)
    ax.set_xticks(x + bar_width)
    ax.set_xticklabels(opts, fontsize=10)
    ax.legend(loc='upper right', frameon=True, fontsize=10)
    ax.grid(True, axis='y', linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    out_file = os.path.join(output_dir, '00_bitness_speedup_analysis.png')
    plt.savefig(out_file, dpi=300)
    plt.close()
    print(f"Generated bitness analysis plot: {out_file}")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, '..'))
    csv_file = os.path.join(root_dir, 'results', 'spec_cpu2017_results.csv')
    plots_dir = os.path.join(root_dir, 'plots')
    os.makedirs(plots_dir, exist_ok=True)
    
    if not os.path.exists(csv_file):
        print(f"Error: CSV file not found at {csv_file}. Please run parse_results.py first.")
        return
        
    data = load_data(csv_file)
    
    # Generate 9 individual benchmark plots
    for bm_name, bm_data in data.items():
        plot_individual_benchmark(bm_name, bm_data, plots_dir)
        
    # Generate summary grid plot
    plot_summary_grid(data, plots_dir)
    
    # Generate bitness comparison plot
    plot_bitness_comparison(data, plots_dir)
    
    print("All plots generated successfully!")

if __name__ == '__main__':
    main()
