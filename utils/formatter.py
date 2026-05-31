import pandas as pd

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
    def format_standard_analysis(results, outcome_name):
        """
        Decodes bitstrings and formats the Standard QCA Minimization results
        into a comprehensive text report.
        """
        conditions = results['conditions']
        report = f"Outcome: {outcome_name}\n"
        
        def format_sol_block(title, data):
            block = f"\n--- {title} ---\n"
            if not data or not data['term_metrics']:
                block += "No solutions found.\n"
                return block
            
            block += f"Solution Consistency: {data['solution_consistency']:.4f}\n"
            block += f"Solution Coverage:    {data['solution_coverage']:.4f}\n\n"
            block += f"{'Term':<30} {'Raw Cov.':>10} {'Unique Cov.':>12} {'Consist.':>10}\n"
            block += "-" * 65 + "\n"
            
            for m in data['term_metrics']:
                # Decode term (bitstring -> condition names)
                parts = []
                for i, char in enumerate(m['term']):
                    if char == '1':
                        parts.append(conditions[i])
                    elif char == '0':
                        parts.append(f"~{conditions[i]}")
                
                term_str = " * ".join(parts) if parts else "1"
                
                block += f"{term_str[:30]:<30} {m['raw_coverage']:>10.4f} {m['unique_coverage']:>12.4f} {m['consistency']:>10.4f}\n"
            return block

        report += format_sol_block("INTERMEDIATE SOLUTION", results['intermediate_metrics'])
        report += format_sol_block("PARSIMONIOUS SOLUTION", results['parsimonious_metrics'])
        report += format_sol_block("COMPLEX SOLUTION", results['complex_metrics'])
        
        return report
