# PQAEF/PQAEF/statistics/report_generator.py (Corrected version with warnings fixed)
# -*- coding: utf-8 -*-
import os
import datetime
import re
from typing import Dict, Any, List, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.font_manager import FontProperties

from ..constant import constant

class ReportGenerator:
    """
    Analyzes processed data to generate a comprehensive and dynamic statistical report.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_dir = self.config['output_dir']
        self.file_prefix = self.config.get('file_prefix', 'statistics')
        os.makedirs(self.output_dir, exist_ok=True)
        self.font_props = self._get_font_properties()
        plt.rcParams['axes.unicode_minus'] = False

    def _get_font_properties(self) -> FontProperties:
        """Loads a bundled font file for CJK character support in plots."""
        try:
            font_path = os.path.join(
                os.path.dirname(__file__), '..', 'resources', 'fonts', 'NotoSansSC-Regular.ttf'
            )
            if os.path.exists(font_path):
                print(f"INFO: Found CJK font at '{font_path}'. Plots will render Chinese characters correctly.")
                return FontProperties(fname=font_path)
            else:
                print("WARNING: CJK font not found. Chinese characters in plots may appear as squares.")
                print(f"To fix this, download a font like 'Noto Sans SC' and place it at: {os.path.abspath(font_path)}")
                return None
        except Exception as e:
            print(f"ERROR: An error occurred while loading the font: {e}")
            return None

    def _flatten_sample_annotations(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        """Flattens the nested annotation dictionary and adds turn count."""
        flat_data = {}
        
        def flatten_dict(d, parent_key='', sep='.'):
            items = []
            for k, v in d.items():
                new_key = parent_key + sep + k if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)

        dialogue_ann = sample.get(constant.KEY_DIALOGUE_ANNOTATION, {})
        flat_data.update(flatten_dict(dialogue_ann))
        flat_data['turn_count'] = len(sample.get(constant.KEY_DIALOGUES, []))
        return flat_data

    def _unpack_list_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Finds columns containing lists and unpacks them into separate columns."""
        print("INFO: Checking for list-based columns to unpack...")
        cols_to_unpack = []
        for col in df.columns:
            first_val = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
            if isinstance(first_val, list):
                cols_to_unpack.append(col)

        for col in cols_to_unpack:
            print(f"INFO: Unpacking list-based column: '{col}'")
            unpacked_cols = pd.DataFrame(df[col].tolist(), index=df.index).add_prefix(f'{col}_')
            df = df.join(unpacked_cols)
            df = df.drop(columns=[col])
        
        return df

    def _plot_histograms_for_numeric_fields(self, df: pd.DataFrame, numeric_fields: List[str]) -> List[str]:
        """Generates and saves a histogram for each specified numeric field."""
        plot_paths = []
        plt.style.use('seaborn-v0_8-whitegrid')
        
        for field in numeric_fields:
            if field == 'turn_count':
                continue

            safe_filename = re.sub(r'[^a-zA-Z0-9_-]', '_', field)
            plot_path = os.path.join(self.output_dir, f"{self.file_prefix}_plot_numeric_{safe_filename}.png")
            
            plt.figure(figsize=(10, 6))
            sns.histplot(df[field].dropna(), kde=True, bins=30)
            
            plt.title(f"Distribution of: {field}", fontsize=16, weight='bold', fontproperties=self.font_props)
            plt.xlabel(field, fontsize=12, fontproperties=self.font_props)
            plt.ylabel('Frequency', fontsize=12, fontproperties=self.font_props)
            plt.tight_layout()
            
            plt.savefig(plot_path, dpi=150)
            plt.close()
            
            plot_paths.append(plot_path)
            print(f"INFO: Numeric plot for '{field}' saved to {plot_path}")
            
        return plot_paths
        
    def _plot_frequency_for_categorical_fields(self, df: pd.DataFrame, categorical_fields: List[str]) -> List[str]:
        """Generates and saves a bar plot for the frequency of each category in the specified categorical fields."""
        plot_paths = []
        plt.style.use('seaborn-v0_8-whitegrid')

        for field in categorical_fields:
            if df[field].nunique() == 0:
                continue

            safe_filename = re.sub(r'[^a-zA-Z0-9_-]', '_', field)
            plot_path = os.path.join(self.output_dir, f"{self.file_prefix}_plot_categorical_{safe_filename}.png")

            plt.figure(figsize=(12, 7))
            
            top_n = 20
            if df[field].nunique() > top_n:
                counts = df[field].value_counts().nlargest(top_n)
                title = f"Top {top_n} Frequencies for: {field}"
            else:
                counts = df[field].value_counts()
                title = f"Frequency of: {field}"

            ax = sns.barplot(x=counts.index, y=counts.values, hue=counts.index, palette='viridis', legend=False)
            
            ax.set_title(title, fontsize=16, weight='bold', fontproperties=self.font_props)
            ax.set_xlabel(field, fontsize=12, fontproperties=self.font_props)
            ax.set_ylabel('Count', fontsize=12, fontproperties=self.font_props)
            
            ax.set_xticklabels(counts.index, rotation=45, ha='right', fontproperties=self.font_props)
            plt.tight_layout()

            plt.savefig(plot_path, dpi=150)
            plt.close()

            plot_paths.append(plot_path)
            print(f"INFO: Categorical plot for '{field}' saved to {plot_path}")
            
        return plot_paths

    def _calculate_turn_distribution(self, df: pd.DataFrame) -> Dict[str, int]:
        bins = {"1-10": 0, "11-20": 0, "21-30": 0, "31-40": 0, "41-50": 0, "51-60": 0, "61-70": 0, "71-80": 0, "81-90": 0, "91-100": 0, "101+": 0}
        for length in df['turn_count']:
            if 1 <= length <= 10: bins["1-10"] += 1
            elif length <= 20: bins["11-20"] += 1
            elif length <= 30: bins["21-30"] += 1
            elif length <= 40: bins["31-40"] += 1
            elif length <= 50: bins["41-50"] += 1
            elif length <= 60: bins["51-60"] += 1
            elif length <= 70: bins["61-70"] += 1
            elif length <= 80: bins["71-80"] += 1
            elif length <= 90: bins["81-90"] += 1
            elif length <= 100: bins["91-100"] += 1
            else: bins["101+"] += 1
        return bins

    def _plot_turn_distribution(self, distribution: Dict[str, int]) -> str:
        plot_path = os.path.join(self.output_dir, f"{self.file_prefix}_plot_turn_distribution.png")
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.figure(figsize=(14, 8))
        palette = sns.color_palette("viridis", len(distribution))
        
        x_labels = list(distribution.keys())
        y_values = list(distribution.values())

        ax = sns.barplot(x=x_labels, y=y_values, hue=x_labels, palette=palette, legend=False)
        
        ax.set_title('Dialogue Turn Length Distribution', fontsize=16, weight='bold', fontproperties=self.font_props)
        ax.set_xlabel('Number of Turns', fontsize=12, fontproperties=self.font_props)
        ax.set_ylabel('Number of Samples', fontsize=12, fontproperties=self.font_props)
        
        ax.set_xticklabels(x_labels, rotation=45, ha='right', fontproperties=self.font_props)
        plt.tight_layout()
        plt.savefig(plot_path, dpi=300)
        plt.close()
        print(f"INFO: Turn distribution plot saved to {plot_path}")
        return plot_path
        
    def _analyze_thematic_distribution(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        results = {}
        primary_col = next((c for c in df.columns if c.endswith('.primary_theme')), None)
        secondary_col = next((c for c in df.columns if c.endswith('.secondary_themes')), None)
        if primary_col:
            primary_counts = df[primary_col].value_counts().reset_index()
            primary_counts.columns = ['Theme', 'Count']
            results['primary'] = primary_counts
        if secondary_col:
            exploded_themes = df[secondary_col].dropna().explode()
            secondary_counts = exploded_themes.value_counts().reset_index()
            secondary_counts.columns = ['Theme', 'Count']
            results['secondary'] = secondary_counts
        return results

    def analyze(self, data: List[Dict[str, Any]], run_metadata: Dict[str, Any]):
        """The main method to perform all analyses and generate reports."""
        if not data:
            print("WARNING: No data provided for analysis.")
            return

        print("\n--- Starting Statistical Analysis ---")
        
        flattened_data = [self._flatten_sample_annotations(s) for s in data]
        df = pd.DataFrame(flattened_data)
        
        df = self._unpack_list_columns(df)
        
        numeric_fields = df.select_dtypes(include=['number']).columns.tolist()
        categorical_fields = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        print("\n[Analysis Step 1/6] Analyzing dialogue turn distribution...")
        turn_dist = self._calculate_turn_distribution(df)
        turn_dist_plot_path = self._plot_turn_distribution(turn_dist)

        print("\n[Analysis Step 2/6] Calculating global statistics for numeric fields...")
        annotation_numeric_fields = [f for f in numeric_fields if f != 'turn_count']
        global_stats = df[annotation_numeric_fields].describe().transpose() if annotation_numeric_fields else pd.DataFrame()
        
        print("\n[Analysis Step 3/6] Generating plots for each numeric field...")
        numeric_plot_paths = self._plot_histograms_for_numeric_fields(df, annotation_numeric_fields)

        print("\n[Analysis Step 4/6] Generating plots for each categorical field...")
        categorical_plot_paths = self._plot_frequency_for_categorical_fields(df, categorical_fields)

        print("\n[Analysis Step 5/6] Performing grouped analysis for each categorical field...")
        all_grouped_stats = {}
        if annotation_numeric_fields:
            for cat_field in categorical_fields:
                print(f"  - Grouping by '{cat_field}'...")
                if df[cat_field].nunique() > 100:
                    print(f"    WARN: Skipping grouped analysis for '{cat_field}' due to high cardinality (>100 unique values).")
                    continue
                
                grouped_df = df.dropna(subset=[cat_field] + annotation_numeric_fields)
                if not grouped_df.empty:
                    stats = grouped_df.groupby(cat_field)[annotation_numeric_fields].agg(
                        ['count', 'mean', 'median', 'std']
                    ).stack(level=0, future_stack=True)
                    all_grouped_stats[cat_field] = stats
        else:
            print("INFO: No numeric fields found. Skipping grouped analysis.")

        print("\n[Analysis Step 6/6] Analyzing specific thematic category distributions...")
        thematic_stats = self._analyze_thematic_distribution(df)
        
        all_plot_paths = [turn_dist_plot_path] + numeric_plot_paths + categorical_plot_paths
        self._write_report_file(data, run_metadata, global_stats, turn_dist, all_plot_paths, all_grouped_stats, thematic_stats)
        
        print("--- Statistical Analysis Finished ---")

    def _write_report_file(self, data, run_metadata, global_stats, turn_dist, plot_paths, all_grouped_stats, thematic_stats):
        """Compiles all analysis results into a single text file."""
        report_path = os.path.join(self.output_dir, f"{self.file_prefix}_report.txt")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write(" PQAEF Full Statistical Report\n")
            f.write("="*80 + "\n")
            f.write(f"Report Generated On: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Samples Analyzed: {len(data)}\n\n")

            f.write("-" * 30 + " Tasks Performed " + "-"*31 + "\n")
            for i, task_info in enumerate(run_metadata.get('tasks_run', [])):
                f.write(f"  {i+1}. {task_info['task_class']} -> '{task_info['config'].get('output_field_name')}'\n")
            f.write("\n")

            f.write("-" * 32 + " Generated Plots " + "-"*31 + "\n")
            f.write(f"  Plots are saved in: {self.output_dir}\n")
            for path in plot_paths:
                f.write(f"  - {os.path.basename(path)}\n")
            f.write("\n")

            f.write("="*80 + "\n")
            f.write(" Part 1: Dialogue Turn Length Distribution\n")
            f.write("="*80 + "\n")
            total_samples = len(data)
            for bin_range, count in turn_dist.items():
                percentage = (count / total_samples) * 100 if total_samples > 0 else 0
                f.write(f"  - {bin_range:<7}: {count:>7} samples ({percentage:6.2f}%)\n")
            f.write("\n")

            if not global_stats.empty:
                f.write("="*80 + "\n")
                f.write(" Part 2: Global Annotation Statistics (Numeric Fields)\n")
                f.write("="*80 + "\n")
                f.write("Summary statistics for all numeric annotation fields across the entire dataset:\n\n")
                f.write(global_stats.to_string(float_format="%.4f"))
                f.write("\n\n")
            
            if all_grouped_stats:
                f.write("="*80 + "\n")
                f.write(f" Part 3: Grouped Analysis by Category\n")
                f.write("="*80 + "\n")
                f.write("Statistics for numeric annotations, grouped by each discovered categorical field.\n\n")

                for cat_field, grouped_data in all_grouped_stats.items():
                    f.write(f" Analysis Grouped by: '{cat_field}' ".center(80, '-') + "\n\n")
                    for group_name, group_stats in grouped_data.groupby(level=0):
                        f.write(f"  Category Value: {group_name}\n")
                        with pd.option_context('display.width', 1000, 'display.max_rows', 100):
                            table_str = group_stats.xs(group_name).reset_index().rename(columns={'level_1': 'Metric'}).to_string(index=False, float_format="%.4f")
                            f.write('\n'.join(f"    {line}" for line in table_str.split('\n')))
                        f.write("\n\n")
            
            if thematic_stats:
                f.write("="*80 + "\n")
                f.write(" Part 4: Specific Thematic Category Distribution\n")
                f.write("="*80 + "\n")
                f.write("Counts of primary and secondary themes identified across the dataset.\n\n")
                
                if 'primary' in thematic_stats and not thematic_stats['primary'].empty:
                    f.write("--- Primary Theme Counts ---\n")
                    f.write(thematic_stats['primary'].to_string(index=False))
                    f.write("\n\n")
                
                if 'secondary' in thematic_stats and not thematic_stats['secondary'].empty:
                    f.write("--- Secondary Theme Counts ---\n")
                    f.write(thematic_stats['secondary'].to_string(index=False))
                    f.write("\n\n")

        print(f"INFO: Full statistical report saved to {report_path}")