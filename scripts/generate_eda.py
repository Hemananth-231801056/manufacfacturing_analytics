"""
EDA Generation Script
======================
Generates comprehensive Exploratory Data Analysis visualizations
saved as PNG files for the project report and web UI.

Usage:
    python scripts/generate_eda.py
"""

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

from backend.ml.data_pipeline import load_and_clean
from backend.ml.feature_engineering import engineer_features
from backend.ml.labeling import create_labels

# Output directory for plots
PLOTS_DIR = os.path.join(PROJECT_ROOT, 'notebooks', 'eda_plots')
os.makedirs(PLOTS_DIR, exist_ok=True)

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
COLORS = {'Approved': '#06D6A0', 'Rework': '#FFD166', 'Rejected': '#EF476F'}


def plot_correlation_heatmap(df):
    """Generate correlation heatmap for top 30 correlated features."""
    print("  Generating correlation heatmap...")
    numeric_df = df.select_dtypes(include=[np.number])
    
    # Get top 30 features by variance
    top_cols = numeric_df.var().nlargest(30).index.tolist()
    corr = numeric_df[top_cols].corr()
    
    fig, ax = plt.subplots(figsize=(14, 12))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, cmap='RdBu_r', center=0, annot=False,
                square=True, linewidths=0.5, ax=ax, vmin=-1, vmax=1,
                cbar_kws={'shrink': 0.8})
    ax.set_title('Feature Correlation Matrix (Top 30 by Variance)', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right', fontsize=7)
    plt.yticks(fontsize=7)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'correlation_heatmap.png'), dpi=150, bbox_inches='tight')
    plt.close()


def plot_cqa_distributions(df):
    """Plot distributions of Critical Quality Attributes."""
    print("  Generating CQA distributions...")
    cqa_cols = ['dissolution_av', 'dissolution_min', 'impurities_total',
                'impurity_o', 'impurity_l', 'residual_solvent']
    existing = [c for c in cqa_cols if c in df.columns]
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    for i, col in enumerate(existing):
        if i < len(axes):
            ax = axes[i]
            data = df[col].dropna()
            ax.hist(data, bins=30, color='#118AB2', alpha=0.7, edgecolor='white')
            ax.set_title(col.replace('_', ' ').title(), fontsize=11, fontweight='bold')
            ax.set_xlabel('Value')
            ax.set_ylabel('Frequency')
            ax.axvline(data.mean(), color='red', linestyle='--', label=f'Mean: {data.mean():.3f}')
            ax.legend(fontsize=8)
    
    # Hide unused axes
    for j in range(len(existing), len(axes)):
        axes[j].set_visible(False)
    
    plt.suptitle('Critical Quality Attribute Distributions', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'cqa_distributions.png'), dpi=150, bbox_inches='tight')
    plt.close()


def plot_process_distributions(df):
    """Plot distributions of key process parameters."""
    print("  Generating process parameter distributions...")
    process_cols = ['main_CompForce_mean', 'stiffness_mean', 'ejection_mean',
                    'tbl_fill_mean', 'tbl_speed_mean', 'fom_mean']
    existing = [c for c in process_cols if c in df.columns]
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    for i, col in enumerate(existing):
        if i < len(axes):
            ax = axes[i]
            data = df[col].dropna()
            ax.hist(data, bins=30, color='#06D6A0', alpha=0.7, edgecolor='white')
            ax.set_title(col.replace('_', ' ').title(), fontsize=11, fontweight='bold')
            ax.set_xlabel('Value')
            ax.set_ylabel('Frequency')
    
    for j in range(len(existing), len(axes)):
        axes[j].set_visible(False)
    
    plt.suptitle('Process Parameter Distributions', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'process_distributions.png'), dpi=150, bbox_inches='tight')
    plt.close()


def plot_raw_material_distributions(df):
    """Plot distributions of raw material quality attributes."""
    print("  Generating raw material distributions...")
    rm_cols = ['api_water', 'api_total_impurities', 'api_content',
               'api_ps05', 'smcc_water', 'lactose_water']
    existing = [c for c in rm_cols if c in df.columns]
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    for i, col in enumerate(existing):
        if i < len(axes):
            ax = axes[i]
            data = df[col].dropna()
            ax.hist(data, bins=25, color='#FFD166', alpha=0.7, edgecolor='white')
            ax.set_title(col.replace('_', ' ').title(), fontsize=11, fontweight='bold')
    
    for j in range(len(existing), len(axes)):
        axes[j].set_visible(False)
    
    plt.suptitle('Raw Material Quality Distributions', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'raw_material_distributions.png'), dpi=150, bbox_inches='tight')
    plt.close()


def plot_missing_values(df):
    """Generate missing value analysis plot."""
    print("  Generating missing values analysis...")
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    
    if len(missing) == 0:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, 'No Missing Values Detected', transform=ax.transAxes,
                ha='center', va='center', fontsize=16, fontweight='bold', color='#06D6A0')
        ax.set_title('Missing Value Analysis', fontsize=14, fontweight='bold')
        ax.axis('off')
    else:
        fig, ax = plt.subplots(figsize=(10, max(4, len(missing) * 0.4)))
        ax.barh(range(len(missing)), missing.values, color='#EF476F', alpha=0.8)
        ax.set_yticks(range(len(missing)))
        ax.set_yticklabels(missing.index, fontsize=9)
        ax.set_xlabel('Number of Missing Values')
        ax.set_title('Missing Value Analysis', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'missing_values.png'), dpi=150, bbox_inches='tight')
    plt.close()


def plot_class_balance(df):
    """Plot quality label class distribution."""
    print("  Generating class balance plot...")
    if 'quality_label' not in df.columns:
        return
    
    counts = df['quality_label'].value_counts()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Bar chart
    bars = ax1.bar(counts.index, counts.values,
                   color=[COLORS.get(l, '#888') for l in counts.index],
                   edgecolor='white', linewidth=1.5)
    ax1.set_title('Class Distribution', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Number of Batches')
    for bar, count in zip(bars, counts.values):
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 5,
                f'{count}', ha='center', va='bottom', fontweight='bold')
    
    # Pie chart
    ax2.pie(counts.values, labels=counts.index, autopct='%1.1f%%',
            colors=[COLORS.get(l, '#888') for l in counts.index],
            startangle=90, textprops={'fontsize': 11})
    ax2.set_title('Class Proportions', fontsize=13, fontweight='bold')
    
    plt.suptitle('Quality Label Distribution', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'class_balance.png'), dpi=150, bbox_inches='tight')
    plt.close()


def plot_boxplots_cqa(df):
    """Box plots for CQA columns to identify outliers."""
    print("  Generating CQA box plots...")
    cqa_cols = ['dissolution_av', 'dissolution_min', 'impurities_total', 'residual_solvent']
    existing = [c for c in cqa_cols if c in df.columns]
    
    fig, axes = plt.subplots(1, len(existing), figsize=(4*len(existing), 6))
    if len(existing) == 1:
        axes = [axes]
    
    for i, col in enumerate(existing):
        data = df[col].dropna()
        bp = axes[i].boxplot(data, patch_artist=True, widths=0.6)
        bp['boxes'][0].set_facecolor('#118AB2')
        bp['boxes'][0].set_alpha(0.6)
        bp['medians'][0].set_color('red')
        axes[i].set_title(col.replace('_', ' ').title(), fontsize=10, fontweight='bold')
        axes[i].set_ylabel('Value')
    
    plt.suptitle('CQA Outlier Analysis (Box Plots)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'boxplots_cqa.png'), dpi=150, bbox_inches='tight')
    plt.close()


def plot_yield_vs_quality(df):
    """Scatter plot of batch yield vs dissolution (quality relationship)."""
    print("  Generating yield vs quality plot...")
    if not all(c in df.columns for c in ['batch_yield', 'dissolution_av']):
        return
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if 'quality_label' in df.columns:
        for label, color in COLORS.items():
            mask = df['quality_label'] == label
            ax.scatter(df.loc[mask, 'batch_yield'], df.loc[mask, 'dissolution_av'],
                      c=color, label=label, alpha=0.6, s=40, edgecolors='white', linewidth=0.5)
        ax.legend()
    else:
        ax.scatter(df['batch_yield'], df['dissolution_av'], alpha=0.5, s=40, c='#118AB2')
    
    ax.set_xlabel('Batch Yield (%)', fontsize=12)
    ax.set_ylabel('Average Dissolution (%)', fontsize=12)
    ax.set_title('Batch Yield vs. Dissolution Rate', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'yield_vs_quality.png'), dpi=150, bbox_inches='tight')
    plt.close()


def plot_weekend_effect(df):
    """Box plot comparing quality metrics for weekend vs weekday production."""
    print("  Generating weekend effect plot...")
    if not all(c in df.columns for c in ['weekend', 'dissolution_av']):
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Dissolution by weekend
    groups = [df[df['weekend'] == 0]['dissolution_av'].dropna(),
              df[df['weekend'] == 1]['dissolution_av'].dropna()]
    bp = axes[0].boxplot(groups, tick_labels=['Weekday', 'Weekend'], patch_artist=True, widths=0.5)
    bp['boxes'][0].set_facecolor('#06D6A0')
    bp['boxes'][1].set_facecolor('#FFD166')
    axes[0].set_title('Dissolution by Production Day', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Average Dissolution (%)')
    
    # Impurities by weekend
    if 'impurities_total' in df.columns:
        groups2 = [df[df['weekend'] == 0]['impurities_total'].dropna(),
                   df[df['weekend'] == 1]['impurities_total'].dropna()]
        bp2 = axes[1].boxplot(groups2, tick_labels=['Weekday', 'Weekend'], patch_artist=True, widths=0.5)
        bp2['boxes'][0].set_facecolor('#06D6A0')
        bp2['boxes'][1].set_facecolor('#FFD166')
        axes[1].set_title('Impurities by Production Day', fontsize=12, fontweight='bold')
        axes[1].set_ylabel('Total Impurities (%)')
    
    plt.suptitle('Weekend Production Effect on Quality', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'weekend_effect.png'), dpi=150, bbox_inches='tight')
    plt.close()


def plot_product_code_quality(df):
    """Quality distribution per product code."""
    print("  Generating product code quality plot...")
    if not all(c in df.columns for c in ['code', 'quality_label']):
        return
    
    ct = pd.crosstab(df['code'], df['quality_label'])
    ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100
    
    fig, ax = plt.subplots(figsize=(14, 6))
    ct_pct.plot(kind='bar', stacked=True, ax=ax,
                color=[COLORS.get(c, '#888') for c in ct_pct.columns],
                edgecolor='white', linewidth=0.5)
    ax.set_xlabel('Product Code', fontsize=12)
    ax.set_ylabel('Percentage (%)', fontsize=12)
    ax.set_title('Quality Distribution by Product Code', fontsize=14, fontweight='bold')
    ax.legend(title='Quality', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'product_code_quality.png'), dpi=150, bbox_inches='tight')
    plt.close()


def main():
    """Generate all EDA plots."""
    print("=" * 70)
    print("  Exploratory Data Analysis — Plot Generation")
    print("=" * 70)
    
    # Load and prepare data
    print("\n[EDA] Loading data...")
    df = load_and_clean()
    df = engineer_features(df)
    
    # Generate plots before labeling (raw data analysis)
    print("\n[EDA] Generating EDA plots...")
    plot_missing_values(df)
    plot_correlation_heatmap(df)
    plot_cqa_distributions(df)
    plot_process_distributions(df)
    plot_raw_material_distributions(df)
    plot_boxplots_cqa(df)
    plot_yield_vs_quality(df)
    plot_weekend_effect(df)
    
    # Label and generate class-specific plots
    print("\n[EDA] Generating label-specific plots...")
    df = create_labels(df)
    plot_class_balance(df)
    plot_yield_vs_quality(df)  # Regenerate with labels
    plot_product_code_quality(df)
    
    print(f"\n[EDA] All EDA plots saved to: {PLOTS_DIR}")
    
    # List generated files
    for f in sorted(os.listdir(PLOTS_DIR)):
        size = os.path.getsize(os.path.join(PLOTS_DIR, f))
        print(f"  - {f} ({size/1024:.1f} KB)")


if __name__ == '__main__':
    main()
