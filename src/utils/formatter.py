# fsQCA Pro
# Copyright (C) 2026 ImmortalSoft
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pandas as pd
import csv
import io

class ResultFormatter:
    @staticmethod
    def format_subset(df: pd.DataFrame) -> str:
        """Formats Subset/Superset analysis results into a clean string table."""
        if df is None or df.empty:
            return "No subset analysis results to display."
        return df.to_string(index=False)

    @staticmethod
    def format_necessity(df: pd.DataFrame) -> str:
        """
        Formats Necessary Conditions analysis results into a clean string table,
        including auditing metrics for relevance and triviality.
        """
        if df is None or df.empty:
            return "No necessary condition analysis results to display."
        
        # Select and order columns for the text report
        cols = ['Condition', 'Consistency', 'Coverage', 'RoN', 'Triviality']
        if all(c in df.columns for c in cols):
            return df[cols].to_string(index=False, formatters={
                'Consistency': '{:.4f}'.format,
                'Coverage': '{:.4f}'.format,
                'RoN': '{:.4f}'.format,
                'Triviality': '{:.4f}'.format
            })
        return df.to_string(index=False)

    @staticmethod
    def format_descriptives(df):
        """Formats descriptive statistics into a clean string table."""
        if df is None or df.empty:
            return "No descriptive statistics to display."
        return df.to_string(index=False)

    @staticmethod
    def format_standard_analysis(results: dict, outcome_name: str) -> str:
        """
        Formats the Standard QCA Minimization results into a comprehensive text report.
        Aligned with Ragin's fsQCA app standards.
        """
        conditions = results.get('conditions', [])
        freq_thresh = results.get('frequency_cutoff', '?')
        consist_thresh = results.get('consistency_cutoff', '?')
        assumptions = results.get('assumptions', {})
        
        report = "**********************\n"
        report += "*TRUTH TABLE ANALYSIS*\n"
        report += "**********************\n\n"
        
        model_str = f"{outcome_name} = f(" + ", ".join(conditions) + ")"
        report += f"Model: {model_str}\n"
        report += "Algorithm: Quine-McCluskey\n\n"

        def format_sol_block(title, data, is_intermediate=False):
            block = f"--- {title} ---\n"
            block += f"frequency cutoff: {freq_thresh}\n"
            block += f"consistency cutoff: {consist_thresh}\n"
            
            if is_intermediate:
                block += "Assumptions:\n"
                if assumptions:
                    for cond, val in assumptions.items():
                        block += f"  {cond} ({val})\n"
                else:
                    block += "  None\n"

            if not data or not data.get('term_metrics'):
                block += "No solution found.\n\n"
                return block

            # High-fidelity alignment to Ragin's classic look
            block += f"{'':<50} raw       unique\n"
            block += f"{'':<50} coverage    coverage   consistency\n"
            block += f"{'':<50} ----------  ----------  ----------\n"

            for m in data['term_metrics']:
                parts = []
                for i, char in enumerate(m['term']):
                    if char == '1':
                        parts.append(conditions[i])
                    elif char == '0':
                        parts.append(f"~{conditions[i]}")
                
                term_str = "*".join(parts) if parts else "1"
                block += f"{term_str:<50} {m['raw_coverage']:<11.6f} {m['unique_coverage']:<11.6f} {m['consistency']:<11.6f}\n"

            block += f"solution coverage: {data['solution_coverage']:.6f}\n"
            block += f"solution consistency: {data['solution_consistency']:.6f}\n\n"
            return block

        # Order: Complex, Parsimonious, Intermediate
        report += format_sol_block("COMPLEX SOLUTION", results.get('complex_metrics'))
        report += format_sol_block("PARSIMONIOUS SOLUTION", results.get('parsimonious_metrics'))
        report += format_sol_block("INTERMEDIATE SOLUTION", results.get('intermediate_metrics'), is_intermediate=True)
        
        return report

    @staticmethod
    def format_truth_table_csv(df: pd.DataFrame) -> str:
        """Formats the Truth Table DataFrame into a CSV string."""
        output = io.StringIO()
        df.to_csv(output, index=False)
        return output.getvalue()

    @staticmethod
    def format_standard_analysis_csv(results: dict, outcome_name: str) -> str:
        """Formats the Standard QCA Minimization results into a CSV string."""
        conditions = results.get('conditions', [])
        freq_thresh = results.get('frequency_cutoff', '?')
        consist_thresh = results.get('consistency_cutoff', '?')
        assumptions = results.get('assumptions', {})

        output = io.StringIO()
        writer = csv.writer(output)
        
        # Meta info
        writer.writerow(["Model", f"{outcome_name} = f(" + ", ".join(conditions) + ")"])
        writer.writerow(["Algorithm", "Quine-McCluskey"])
        writer.writerow(["Frequency Cutoff", freq_thresh])
        writer.writerow(["Consistency Cutoff", consist_thresh])
        
        if assumptions:
            writer.writerow(["Assumptions"])
            for cond, val in assumptions.items():
                writer.writerow(["", cond, val])
        
        writer.writerow([])
        
        def write_sol_block(title, data):
            if not data or not data.get('term_metrics'):
                writer.writerow([title])
                writer.writerow(["No solutions found."])
                writer.writerow([])
                return
            
            writer.writerow([title])
            writer.writerow(["Solution Consistency", f"{data['solution_consistency']:.6f}"])
            writer.writerow(["Solution Coverage", f"{data['solution_coverage']:.6f}"])
            writer.writerow(["Term", "Raw Coverage", "Unique Coverage", "Consistency"])
            
            for m in data['term_metrics']:
                parts = []
                for i, char in enumerate(m['term']):
                    if char == '1':
                        parts.append(conditions[i])
                    elif char == '0':
                        parts.append(f"~{conditions[i]}")
                
                term_str = "*".join(parts) if parts else "1"
                writer.writerow([
                    term_str, 
                    f"{m['raw_coverage']:.6f}", 
                    f"{m['unique_coverage']:.6f}", 
                    f"{m['consistency']:.6f}"
                ])
            writer.writerow([])

        # Sequence aligned with the UI/TXT: Complex, Parsimonious, Intermediate
        write_sol_block("COMPLEX SOLUTION", results.get('complex_metrics'))
        write_sol_block("PARSIMONIOUS SOLUTION", results.get('parsimonious_metrics'))
        write_sol_block("INTERMEDIATE SOLUTION", results.get('intermediate_metrics'))
        
        return output.getvalue()
