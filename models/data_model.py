import pandas as pd
import numpy as np
import os
import itertools
from itertools import combinations
import re
import json
import logging
from typing import Dict, Any, Tuple, Optional, List
from models.minimizer import QCAMinimizer
from utils.logger import ResearchLogger

class QCADataModel:
    def __init__(self) -> None:
        """Initializes the QCA Data Model with empty storage for data and metadata."""
        self.dataframe: Optional[pd.DataFrame] = None
        self.truth_table_df: Optional[pd.DataFrame] = None
        self._full_dataframe: Optional[pd.DataFrame] = None
        self.calibration_metadata: Dict[str, Any] = {} # Metadata for calibrated columns
        self.sanitization_log: List[str] = [] # Track ingestion actions (PRD 005)
        self.logger = ResearchLogger()

    def load_file(self, filepath: str) -> Tuple[bool, str]:
        """
        Reads .csv and tab-delimited .dat files into a pandas DataFrame.
        Applies dynamic sanitization and logs all actions for transparency.
        
        Args:
            filepath: Path to the data file.

        Returns:
            A tuple of (success, message).
        """
        if not os.path.exists(filepath):
            return False, f"Error: File '{filepath}' does not exist."

        self.sanitization_log = [] # Reset log for new load
        _, ext = os.path.splitext(filepath)
        
        try:
            if ext.lower() == '.csv':
                df = pd.read_csv(filepath)
            elif ext.lower() == '.dat':
                df = pd.read_csv(filepath, sep='\t')
            else:
                return False, f"Error: Unsupported file extension '{ext}'."
            
            initial_rows = len(df)
            initial_cols = list(df.columns)
            
            # 1. Clean column names (PRD 005)
            new_columns = []
            for col in df.columns:
                clean_name = str(col).replace(' ', '_')
                clean_name = re.sub(r'[^a-zA-Z0-9_]', '', clean_name)
                
                if clean_name != str(col):
                    self.sanitization_log.append(
                        f"Renamed variable '{col}' to '{clean_name}'. "
                        f"Reason: Alphanumeric enforcement for Boolean compatibility."
                    )
                new_columns.append(clean_name)
            df.columns = new_columns
            
            # 2. Dynamic numeric conversion
            for col in df.columns:
                orig_count = df[col].count()
                if orig_count == 0:
                    continue
                
                temp_numeric = pd.to_numeric(df[col], errors='coerce')
                new_count = temp_numeric.count()
                
                # If conversion is mostly successful, apply it
                if (new_count / orig_count) > 0.5:
                    if df[col].dtype != temp_numeric.dtype:
                        self.sanitization_log.append(
                            f"Converted variable '{col}' to numeric. "
                            f"Reason: Column contains mostly numerical data."
                        )
                    df[col] = temp_numeric
                
                # Check for missing values in numeric columns
                null_count = df[col].isna().sum()
                if null_count > 0:
                    self.sanitization_log.append(
                        f"Found {null_count} missing value(s) in '{col}'. "
                        f"Reason: Standardization to NaN for complete-case analysis."
                    )
            
            # 3. Complete-case analysis
            df.dropna(inplace=True)
            self.dataframe = df
            self._full_dataframe = None 
            
            final_rows = len(self.dataframe)
            dropped_rows = initial_rows - final_rows
            
            if dropped_rows > 0:
                self.sanitization_log.append(
                    f"Dropped {dropped_rows} row(s) from the dataset. "
                    f"Reason: Complete-case analysis (rows contained missing/invalid data)."
                )
            
            # 4. Load Metadata (PRD 004 Persistence)
            self.calibration_metadata = {}
            meta_path = filepath + ".meta.json"
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, 'r', encoding='utf-8') as f:
                        self.calibration_metadata = json.load(f)
                    self.sanitization_log.append(
                        f"Loaded calibration metadata for {len(self.calibration_metadata)} variables. "
                        f"Reason: Restoring theoretical context and anchors."
                    )
                except Exception as e:
                    print(f"Warning: Could not load metadata: {e}")

            success_msg = f"Successfully loaded {filepath}. Total cases: {final_rows}."
            return True, success_msg
        except Exception as e:
            return False, f"Error loading file: {str(e)}"

    def save_file(self, dataframe: pd.DataFrame, filepath: str) -> Tuple[bool, str]:
        """
        Saves a pandas DataFrame to a file and persists calibration metadata.
        
        Args:
            dataframe: The DataFrame to save.
            filepath: Target file path.

        Returns:
            A tuple of (success, message).
        """
        _, ext = os.path.splitext(filepath)
        try:
            if ext.lower() == '.csv':
                dataframe.to_csv(filepath, index=False)
            elif ext.lower() == '.dat':
                dataframe.to_csv(filepath, sep='\t', index=False)
            else:
                return False, f"Error: Unsupported file extension '{ext}' for saving."
            
            # Save Metadata (PRD 004 Persistence)
            if self.calibration_metadata:
                meta_path = filepath + ".meta.json"
                try:
                    with open(meta_path, 'w', encoding='utf-8') as f:
                        json.dump(self.calibration_metadata, f, indent=4)
                except Exception as e:
                    return True, f"Data saved, but metadata failed: {e}"
            
            return True, f"Successfully saved to {filepath}"
        except Exception as e:
            return False, f"Error saving file: {str(e)}"

    def calibrate_variable(self, source_col, new_col, p_full, p_cross, p_non, rationale=""):
        """
        Calculates fuzzy membership scores using the fsQCA log-odds method.
        Stores calibration metadata for transparency.
        """
        if self.dataframe is None:
            return False, "Error: No data loaded."
        
        if source_col not in self.dataframe.columns:
            return False, f"Error: Column '{source_col}' not found."

        try:
            data = self.dataframe[source_col].values
            
            # 1. Calculate deviation from crossover
            deviation = data - p_cross
            
            # 2. Calculate scalars
            # For upper half (>= cross): deviation * scalar_upper = 3.0 at p_full
            # scalar_upper = 3.0 / (p_full - p_cross)
            scalar_upper = 3.0 / (p_full - p_cross)
            
            # For lower half (< cross): deviation * scalar_lower = -3.0 at p_non
            # scalar_lower = -3.0 / (p_non - p_cross)
            scalar_lower = -3.0 / (p_non - p_cross)
            
            # 3. Apply scalars to get log-odds
            log_odds = np.where(deviation >= 0, 
                                deviation * scalar_upper, 
                                deviation * scalar_lower)
            
            # 4. Apply logistic function
            self.dataframe[new_col] = 1 / (1 + np.exp(-log_odds))
            
            # 5. Store metadata (PRD 004)
            self.calibration_metadata[new_col] = {
                'source': source_col,
                'anchors': {'full': p_full, 'cross': p_cross, 'non': p_non},
                'rationale': rationale
            }
            
            # 6. Log action (PRD 009)
            self.logger.log_action(
                category="CALIBRATION",
                description=f"Calibrated '{source_col}' into fuzzy set '{new_col}' using direct method.",
                metadata={
                    "source": source_col,
                    "target": new_col,
                    "anchors": {"full": p_full, "cross": p_cross, "non": p_non},
                    "rationale": rationale
                }
            )
            
            return True, f"Successfully calibrated '{source_col}' into '{new_col}'"
        except Exception as e:
            return False, f"Error during calibration: {str(e)}"

    def dichotomize_variable(self, source_col: str, threshold: float, new_col: str, rationale: str = "") -> Tuple[bool, str]:
        """
        Converts a continuous or fuzzy-set variable into a crisp set (0/1).
        
        Args:
            source_col: Name of the source variable.
            threshold: The value above which cases are coded as 1.
            new_col: Name of the new crisp variable.
            rationale: Theoretical justification for the threshold.
            
        Returns:
            A tuple of (success, message).
        """
        if self.dataframe is None:
            return False, "Error: No data loaded."

        if source_col not in self.dataframe.columns:
            return False, f"Error: Column '{source_col}' not found."

        try:
            # Cases > threshold are 1, <= threshold are 0 (Standard Ragin practice)
            self.dataframe[new_col] = (self.dataframe[source_col] > threshold).astype(int)

            # Store metadata (PRD 008)
            self.calibration_metadata[new_col] = {
                'type': 'dichotomization',
                'source': source_col,
                'threshold': threshold,
                'rationale': rationale
            }

            # 6. Log action (PRD 009)
            self.logger.log_action(
                category="DICHOTOMIZATION",
                description=f"Dichotomized '{source_col}' into crisp set '{new_col}' with threshold {threshold}.",
                metadata={
                    "source": source_col,
                    "target": new_col,
                    "threshold": threshold,
                    "rationale": rationale
                }
            )

            return True, f"Successfully dichotomized '{source_col}' into '{new_col}' with threshold {threshold}."
        except Exception as e:
            return False, f"Error during dichotomization: {str(e)}"

    def get_descriptives(self, columns):
        """
        Calculates descriptive statistics for the selected columns.
        Returns a formatted string of results.
        """
        if self.dataframe is None:
            return "Error: No data loaded."
        
        try:
            # Filter for numeric columns only among selected
            valid_cols = [c for c in columns if c in self.dataframe.columns]
            if not valid_cols:
                return "No valid columns selected."
            
            stats = self.dataframe[valid_cols].agg(['mean', 'std', 'min', 'max', 'count']).transpose()
            stats.columns = ['Mean', 'Std.Dev', 'Min', 'Max', 'N']
            
            output = f"{'Variable':<20} {'Mean':>10} {'Std.Dev':>10} {'Min':>10} {'Max':>10} {'N':>5}\n"
            output += "-" * 70 + "\n"
            
            for var, row in stats.iterrows():
                output += f"{var[:20]:<20} {row['Mean']:>10.3f} {row['Std.Dev']:>10.3f} {row['Min']:>10.3f} {row['Max']:>10.3f} {int(row['N']):>5}\n"
            
            return output
        except Exception as e:
            return f"Error calculating descriptives: {str(e)}"

    def generate_truth_table(self, conditions, outcome, negate_outcome=False):
        """
        Generates a Truth Table for the given conditions and outcome.
        Includes advanced consistency metrics and case tracking.
        """
        if self.dataframe is None:
            return None
        
        # Limit to prevent memory/performance issues
        if len(conditions) > 10:
            raise ValueError("Too many conditions. Maximum allowed is 10 to prevent memory crashes.")
        
        total_cases = len(self.dataframe)
        
        # 1. Generate all 2^k binary combinations
        k = len(conditions)
        combinations = list(itertools.product([0, 1], repeat=k))
        
        rows = []
        outcome_data = self.dataframe[outcome].values
        if negate_outcome:
            outcome_data = 1 - outcome_data
        
        case_ids = self.dataframe.iloc[:, 0].values
        
        for combo in combinations:
            # 2. Calculate fuzzy membership for each case in this specific combination
            # Start with a series of 1s (identity for min)
            membership = np.ones(len(self.dataframe))
            
            for i, val in enumerate(combo):
                col_data = self.dataframe[conditions[i]].values
                if val == 1:
                    membership = np.minimum(membership, col_data)
                else:
                    membership = np.minimum(membership, 1 - col_data)
            
            # 3. Calculate frequency (membership > 0.5)
            frequency = np.sum(membership > 0.5)
            freq_pct = round((frequency / total_cases) * 100)
            
            # 4. Calculate consistency metrics
            sum_membership = np.sum(membership)
            sum_min_xy = np.sum(np.minimum(membership, outcome_data))
            
            # PRI Consistency
            # Formula: (sum(min(X, Y)) - sum(min(X, Y, ~Y))) / (sum(X) - sum(min(X, Y, ~Y)))
            sum_min_xy_noty = np.sum(np.minimum(membership, np.minimum(outcome_data, 1 - outcome_data)))
            denominator_pri = sum_membership - sum_min_xy_noty
            pri_consist = (sum_min_xy - sum_min_xy_noty) / denominator_pri if denominator_pri > 0 else 0.0
            
            # SYM Consistency (Symmetric standard formula)
            # Formula: (sum(min(X, Y)) - sum(min(X, 1-X))) / (sum(X) - sum(min(X, 1-X)))
            sym_penalty = np.sum(np.minimum(membership, 1 - membership))
            denominator_sym = sum_membership - sym_penalty
            sym_consist = (sum_min_xy - sym_penalty) / denominator_sym if denominator_sym > 0 else 0.0
                
            # Case tracking
            matching_cases = case_ids[membership > 0.5]
            cases_str = ", ".join(map(str, matching_cases))

            # Store result
            row_dict = {conditions[i]: combo[i] for i in range(k)}
            row_dict['frequency'] = f"{frequency} ({freq_pct}%)"
            row_dict['_raw_freq'] = frequency  # Hidden helper for thresholds
            row_dict['raw_consistency'] = sum_min_xy / sum_membership if sum_membership > 0 else 0.0
            row_dict['pri_consist'] = pri_consist
            row_dict['sym_consist'] = sym_consist
            row_dict['cases'] = cases_str
            rows.append(row_dict)
            
        # Return as DataFrame sorted by raw frequency descending
        tt_df = pd.DataFrame(rows)
        tt_df = tt_df.sort_values(by='_raw_freq', ascending=False).reset_index(drop=True)
        
        # Add outcome_code column
        tt_df['outcome_code'] = ''
        self.truth_table_df = tt_df
        
        return self.truth_table_df

    def edit_truth_table_row(self, index, new_code):
        """
        Updates the outcome_code at the specified index in the truth table.
        """
        if self.truth_table_df is not None and 0 <= index < len(self.truth_table_df):
            self.truth_table_df.at[index, 'outcome_code'] = new_code
            return True
        return False

    def delete_truth_table_row(self, index):
        """Drops a single row at the specified index."""
        if self.truth_table_df is not None and 0 <= index < len(self.truth_table_df):
            self.truth_table_df.drop(index, inplace=True)
            self.truth_table_df.reset_index(drop=True, inplace=True)
            return True
        return False

    def delete_truth_table_rows_to_end(self, index):
        """Drops all rows from the specified index to the end."""
        if self.truth_table_df is not None and 0 <= index < len(self.truth_table_df):
            self.truth_table_df = self.truth_table_df.iloc[:index].reset_index(drop=True)
            return True
        return False

    def delete_truth_table_rows_from_start(self, index):
        """Drops all rows from the start up to and including the specified index."""
        if self.truth_table_df is not None and 0 <= index < len(self.truth_table_df):
            self.truth_table_df = self.truth_table_df.iloc[index+1:].reset_index(drop=True)
            return True
        return False


    def delete_and_code(self, freq_thresh, consist_thresh):
        """
        Filters the truth table by frequency and automatically codes the outcome.
        """
        if self.truth_table_df is None:
            return False
            
        # Keep rows >= frequency threshold
        self.truth_table_df = self.truth_table_df[self.truth_table_df['_raw_freq'] >= freq_thresh].reset_index(drop=True)
        
        # Code outcome: 1 if consist >= threshold, else 0
        self.truth_table_df['outcome_code'] = self.truth_table_df['raw_consistency'].apply(
            lambda x: '1' if x >= consist_thresh else '0'
        )

        # Sort by outcome_code (1 before 0) and then by raw_consistency (descending)
        self.truth_table_df = self.truth_table_df.sort_values(
            by=['outcome_code', 'raw_consistency'],
            ascending=[False, False]
        ).reset_index(drop=True)

        return True

    def auto_calculate_thresholds(self, column_name):
        """
        Calculates suggested thresholds (95th, 50th, 5th percentiles) for a column.
        Returns a tuple: (p_full, p_cross, p_non)
        """
        if self.dataframe is None or column_name not in self.dataframe.columns:
            return None
        
        try:
            p_full = self.dataframe[column_name].quantile(0.95)
            p_cross = self.dataframe[column_name].quantile(0.50)
            p_non = self.dataframe[column_name].quantile(0.05)
            return (p_full, p_cross, p_non)
        except Exception:
            return None

    def auto_calibrate_all(self):
        """
        Automatically calibrates all numeric variables using percentile thresholds.
        """
        if self.dataframe is None:
            return False, "Error: No data loaded."

        numeric_cols = self.dataframe.select_dtypes(include=['number']).columns
        count = 0
        
        for col in numeric_cols:
            # Skip if already a fuzzy column
            if col.startswith('f_'):
                continue
                
            thresholds = self.auto_calculate_thresholds(col)
            if thresholds:
                p_full, p_cross, p_non = thresholds
                # Use a standard rationale for batch calibration
                rationale = f"Automated calibration using sample percentiles: Full={p_full:.3f} (95th), Cross={p_cross:.3f} (50th), Non={p_non:.3f} (5th)."
                success, _ = self.calibrate_variable(col, f"f_{col}", p_full, p_cross, p_non, rationale=rationale)
                if success:
                    count += 1
                    
        return True, f"Successfully auto-calibrated {count} numeric variables."


    def run_standard_analysis(self, truth_table_df, freq_thresh, consist_thresh, assumptions_dict=None, analysis_config=None, tie_breaker_callback=None):
        """
        Executes standard QCA minimization (Complex, Parsimonious, and Intermediate solutions).
        Uses the provided truth_table_df which should include 'outcome_code'.
        analysis_config: dictionary mapping '1', '0', '-', and 'rem' to 'True', 'False', or 'Don't Cares'.
        tie_breaker_callback: optional callback to resolve tied PIs during greedy cover.
        """
        df = truth_table_df

        # Identify non-condition columns
        condition_cols = [c for c in df.columns if c not in ['frequency', '_raw_freq', 'raw_consistency', 'outcome_code', 'pri_consist', 'sym_consist', 'cases']]

        # 1. Gather pos_minterms, neg_minterms, and explicit_dc from the truth table
        if analysis_config:
            def get_state(code):
                key = code if code != '' else 'rem'
                return analysis_config.get(key, 'False')

            pos_mask = df['outcome_code'].apply(lambda x: get_state(x) == 'True')
            neg_mask = df['outcome_code'].apply(lambda x: get_state(x) == 'False')
            dc_mask = df['outcome_code'].apply(lambda x: get_state(x) == "Don't Cares")
            
            # Special case for uncoded rows ('') if not explicitly handled by 'rem' key as 'True' or 'Don't Cares'
            if analysis_config.get('rem') not in ['True', "Don't Cares"]:
                auto_pos = (df['outcome_code'] == '') & (df['_raw_freq'] >= freq_thresh) & (df['raw_consistency'] >= consist_thresh)
                auto_neg = (df['outcome_code'] == '') & ((df['_raw_freq'] < freq_thresh) | (df['raw_consistency'] < consist_thresh))
                pos_mask = pos_mask | auto_pos
                neg_mask = neg_mask | auto_neg
        else:
            # Fallback to current hardcoded logic
            pos_mask = (df['outcome_code'] == '1') | \
                       ((df['outcome_code'] == '') & (df['_raw_freq'] >= freq_thresh) & (df['raw_consistency'] >= consist_thresh))
            
            neg_mask = (df['outcome_code'] == '0') | \
                       ((df['outcome_code'] == '') & (df['_raw_freq'] >= freq_thresh) & (df['raw_consistency'] < consist_thresh))

            dc_mask = (df['outcome_code'] == '-')

        def df_to_bitstrings(df_subset, cols):
            bitstrings = set()
            for row in df_subset.itertuples(index=False):
                s = "".join(str(int(getattr(row, c))) for c in cols)
                bitstrings.add(s)
            return bitstrings

        pos_minterms = df_to_bitstrings(df[pos_mask], condition_cols)
        neg_minterms = df_to_bitstrings(df[neg_mask], condition_cols)
        explicit_dc = df_to_bitstrings(df[dc_mask], condition_cols)

        if len(pos_minterms) == 0:
            raise ValueError("Error: No configurations passed the frequency and consistency thresholds (The 1-Matrix is empty). Try lowering your thresholds.")

        # 2. Mathematically calculate ALL possible remainders
        k = len(condition_cols)
        all_possible = {"".join(seq) for seq in itertools.product("01", repeat=k)}
        
        # Remainders = all - (pos + neg)
        math_remainders = all_possible - pos_minterms - neg_minterms
        
        # 3. Filter easy counterfactuals for intermediate solution
        easy_minterms = []
        if assumptions_dict:
            # Pre-calculate which bits are present at each index across all pos_minterms
            pos_bits_at_index = []
            for i in range(len(condition_cols)):
                bits = {pm[i] for pm in pos_minterms}
                pos_bits_at_index.append(bits)

            for rem in math_remainders:
                is_easy = True
                for i, cond in enumerate(condition_cols):
                    assumption = assumptions_dict.get(cond, "Present or Absent")
                    if assumption == "Present" and rem[i] == '0':
                        is_easy = False
                        break
                    elif assumption == "Absent" and rem[i] == '1':
                        is_easy = False
                        break
                    elif assumption == "Present or Absent":
                        # Remainder must match the bit of at least one positive minterm at this index
                        if rem[i] not in pos_bits_at_index[i]:
                            is_easy = False
                            break
                if is_easy:
                    easy_minterms.append(rem)
        else:
            easy_minterms = []

        # 4. Instantiate minimizer
        minimizer = QCAMinimizer()
        
        # 5. Complex Solution (Only explicit don't cares from truth table)
        complex_sol = minimizer.minimize(list(pos_minterms), list(explicit_dc), tie_breaker_callback=tie_breaker_callback)
        
        # 6. Parsimonious Solution (All mathematical remainders)
        parsimonious_sol = minimizer.minimize(list(pos_minterms), list(math_remainders), tie_breaker_callback=tie_breaker_callback)

        # 7. Intermediate Solution (Only easy remainders)
        intermediate_sol = minimizer.minimize(list(pos_minterms), list(easy_minterms), tie_breaker_callback=tie_breaker_callback)
        
        # 8. Log action (PRD 009)
        self.logger.log_action(
            category="MINIMIZATION",
            description=f"Performed Quine-McCluskey minimization for outcome '{outcome_code_col if 'outcome_code_col' in locals() else 'Outcome'}'.",
            metadata={
                "conditions": condition_cols,
                "frequency_threshold": freq_thresh,
                "consistency_threshold": consist_thresh,
                "assumptions": assumptions_dict
            }
        )
        
        return {
            "conditions": condition_cols,
            "complex": complex_sol,
            "parsimonious": parsimonious_sol,
            "intermediate": intermediate_sol
        }

    def calculate_metrics(self, solution_terms, conditions, outcome_col):
        """
        Calculates consistency and coverage metrics for a solution.
        """
        if self.dataframe is None:
            return None

        outcome_data = self.dataframe[outcome_col].values
        sum_outcome = np.sum(outcome_data)
        if sum_outcome == 0:
            return None

        def get_term_membership(term, conds):
            membership = np.ones(len(self.dataframe))
            for i, char in enumerate(term):
                if char == '1':
                    membership = np.minimum(membership, self.dataframe[conds[i]].values)
                elif char == '0':
                    membership = np.minimum(membership, 1 - self.dataframe[conds[i]].values)
            return membership

        # 1. Calculate membership for each term
        term_memberships = [get_term_membership(term, conditions) for term in solution_terms]
        
        # 2. Overall solution membership (OR / maximum)
        if term_memberships:
            solution_membership = np.max(term_memberships, axis=0)
        else:
            solution_membership = np.zeros(len(self.dataframe))

        # 3. Solution Consistency
        sum_sol = np.sum(solution_membership)
        sol_consist = np.sum(np.minimum(solution_membership, outcome_data)) / sum_sol if sum_sol > 0 else 0.0
        
        # 4. Solution Coverage
        sol_cover = np.sum(np.minimum(solution_membership, outcome_data)) / sum_outcome

        # 5. Individual Term Metrics
        term_metrics = []
        for i, term in enumerate(solution_terms):
            tm = term_memberships[i]
            sum_tm = np.sum(tm)
            
            raw_cover = np.sum(np.minimum(tm, outcome_data)) / sum_outcome
            consist = np.sum(np.minimum(tm, outcome_data)) / sum_tm if sum_tm > 0 else 0.0
            
            # 6. Unique Coverage
            # Solution coverage without this term
            other_terms = term_memberships[:i] + term_memberships[i+1:]
            if other_terms:
                other_sol_membership = np.max(other_terms, axis=0)
                other_sol_cover = np.sum(np.minimum(other_sol_membership, outcome_data)) / sum_outcome
            else:
                other_sol_cover = 0.0
            
            unique_cover = sol_cover - other_sol_cover
            
            term_metrics.append({
                "term": term,
                "raw_coverage": raw_cover,
                "consistency": consist,
                "unique_coverage": unique_cover
            })

        return {
            "solution_consistency": sol_consist,
            "solution_coverage": sol_cover,
            "term_metrics": term_metrics
        }

    def calculate_necessary_conditions(self, conditions: List[str], outcome: str, negate_outcome: bool = False) -> Optional[pd.DataFrame]:
        """
        Calculates necessity consistency, coverage, and relevance for each condition expression.
        
        Supports fuzzy OR via '+' (e.g., 'A + B') and negation via '~'.
        Includes Relevance of Necessity (RoN) and Triviality auditing (PRD 006).

        Args:
            conditions: List of condition expressions to test.
            outcome: The target outcome variable.
            negate_outcome: Whether to test for the absence of the outcome.

        Returns:
            A pandas DataFrame with results, or None if calculation is impossible.
        """
        if self.dataframe is None:
            return None
            
        outcome_data = self.dataframe[outcome].values
        if negate_outcome:
            outcome_data = 1 - outcome_data
            
        sum_outcome = np.sum(outcome_data)
        if sum_outcome == 0:
            return None
            
        results = []
        
        for expr in conditions:
            # Split by '+' for fuzzy OR
            terms = [t.strip() for t in expr.split('+')]
            term_arrays = []
            
            for t in terms:
                if t.startswith('~'):
                    col_name = t[1:]
                    if col_name in self.dataframe.columns:
                        term_arrays.append(1 - self.dataframe[col_name].values)
                else:
                    if t in self.dataframe.columns:
                        term_arrays.append(self.dataframe[t].values)
            
            if not term_arrays:
                continue
                
            # Combine terms using fuzzy OR (MAX)
            cond_data = np.maximum.reduce(term_arrays)
            
            # 1. Consistency: sum(min(X, Y)) / sum(Y)
            consist = np.sum(np.minimum(cond_data, outcome_data)) / sum_outcome
            
            # 2. Coverage (Standard): sum(min(X, Y)) / sum(X)
            sum_cond = np.sum(cond_data)
            cover = np.sum(np.minimum(cond_data, outcome_data)) / sum_cond if sum_cond > 0 else 0.0
            
            # 3. Relevance of Necessity (RoN): sum(min(1-X, 1-Y)) / sum(1-X)
            # This measure detects triviality (conditions that are present everywhere)
            sum_not_cond = np.sum(1 - cond_data)
            ron = np.sum(np.minimum(1 - cond_data, 1 - outcome_data)) / sum_not_cond if sum_not_cond > 0 else 0.0
            
            # 4. Triviality Proxy (Avg Membership)
            # High avg membership (> 0.8) often flags potentially trivial conditions
            triviality = np.mean(cond_data)
            
            results.append({
                'Condition': expr,
                'Consistency': consist,
                'Coverage': cover,
                'RoN': ron,
                'Triviality': triviality
            })
            
        df_res = pd.DataFrame(results)
        if not df_res.empty:
            return df_res.sort_values(by='Consistency', ascending=False)
        return df_res

    def compute_variable(self, target_col, expression):
        """
        Evaluates a pandas expression and creates a new column in the dataframe.
        """
        if self.dataframe is None:
            return False, "Error: No data loaded."
        
        try:
            # Use pandas eval for efficient and safe computation
            # engine='python' allows for more flexible expressions if needed
            self.dataframe[target_col] = self.dataframe.eval(expression)
            return True, f"Successfully computed variable '{target_col}'"
        except Exception as e:
            return False, f"Error computing variable: {str(e)}"

    def apply_recode(self, source_col, target_col, rules):
        """
        Applies a series of recoding rules to a source column and saves to target column.
        Rules are applied sequentially to unprocessed rows.
        """
        if self.dataframe is None:
            return False, "Error: No data loaded."
        
        if source_col not in self.dataframe.columns:
            return False, f"Error: Source column '{source_col}' not found."

        try:
            # Create a working copy
            new_data = self.dataframe[source_col].copy()
            # Track processed rows to ensure sequential logic (first match wins)
            processed = pd.Series(False, index=self.dataframe.index)

            for rule in rules:
                r_type = rule.get('type')
                new_val = rule.get('new')
                
                # Convert 'missing' string to actual NaN if needed
                if new_val == 'missing':
                    new_val = np.nan

                condition_mask = None
                
                if r_type == 'value':
                    condition_mask = (new_data == rule['old'])
                elif r_type == 'missing':
                    condition_mask = new_data.isna()
                elif r_type == 'range':
                    condition_mask = (new_data >= rule['min']) & (new_data <= rule['max'])
                elif r_type == 'range_lowest':
                    condition_mask = (new_data <= rule['max'])
                elif r_type == 'range_highest':
                    condition_mask = (new_data >= rule['min'])
                elif r_type == 'otherwise':
                    condition_mask = pd.Series(True, index=self.dataframe.index)
                
                if condition_mask is not None:
                    # Apply only to rows not already handled by a previous rule
                    actual_mask = condition_mask & ~processed
                    new_data.loc[actual_mask] = new_val
                    processed = processed | actual_mask

            self.dataframe[target_col] = new_data
            return True, f"Successfully recoded '{source_col}' into '{target_col}'"
            
        except Exception as e:
            return False, f"Error during recode: {str(e)}"

    def evaluate_term(self, term):
        """Helper to fetch fuzzy membership for a term, handling negation."""
        if term.startswith('~'):
            col = term[1:]
            return 1 - self.dataframe[col].values
        return self.dataframe[term].values

    def run_subset_superset_analysis(self, conditions, outcome, negate_outcome=False):
        """
        Systematically tests all combinations of conditions as subsets of the outcome.
        """
        if self.dataframe is None:
            return None
            
        outcome_data = self.dataframe[outcome].values
        if negate_outcome:
            outcome_data = 1 - outcome_data
            
        sum_y = np.sum(outcome_data)
        if sum_y == 0:
            return None
            
        results = []
        
        # Generate all combinations of length 1 to N
        for r in range(1, len(conditions) + 1):
            for combo in combinations(conditions, r):
                expr_str = " * ".join(combo)
                
                # Calculate fuzzy AND (MIN) for the combination
                term_arrays = [self.evaluate_term(c) for c in combo]
                if len(term_arrays) > 1:
                    membership = np.minimum.reduce(term_arrays)
                else:
                    membership = term_arrays[0]
                
                sum_x = np.sum(membership)
                sum_min_xy = np.sum(np.minimum(membership, outcome_data))
                
                # Metrics
                subset_consist = sum_min_xy / sum_x if sum_x > 0 else 0.0
                subset_cover = sum_min_xy / sum_y if sum_y > 0 else 0.0
                combined = subset_consist * subset_cover
                
                results.append({
                    'terms': expr_str,
                    'consistency': subset_consist,
                    'coverage': subset_cover,
                    'combined': combined
                })
        
        df_res = pd.DataFrame(results)
        if not df_res.empty:
            return df_res.sort_values(by='consistency', ascending=False)
        return df_res

    def new_dataset(self):
        """Initializes a new empty dataset."""
        self.dataframe = pd.DataFrame()
        self._full_dataframe = None
        return True, "New dataset created."

    def add_case(self):
        """Appends a new empty row to the dataset."""
        if self.dataframe is not None:
            # If dataframe is empty but we want to add a case, 
            # we usually need at least one column to represent a row.
            if self.dataframe.empty and len(self.dataframe.columns) == 0:
                return False
            
            # Create a new row with NaNs
            new_row = {col: np.nan for col in self.dataframe.columns}
            self.dataframe = pd.concat([self.dataframe, pd.DataFrame([new_row])], ignore_index=True)
            return True
        return False

    def select_if(self, condition):
        """
        Filters the dataframe based on a Boolean condition.
        Saves the current full dataframe for later restoration.
        """
        if self.dataframe is None:
            return False, "Error: No data loaded."

        try:
            # Take snapshot if this is the first selection
            if self._full_dataframe is None:
                self._full_dataframe = self.dataframe.copy()
            
            # Apply filter to the FULL dataset to avoid nested filtering confusion
            filtered = self._full_dataframe.query(condition)
            self.dataframe = filtered.reset_index(drop=True)
            return True, f"Selection applied. {len(self.dataframe)} cases remain."
            
        except Exception as e:
            return False, f"Invalid condition: {str(e)}"

    def cancel_selection(self):
        """Restores the full dataframe from before selection was applied."""
        if self._full_dataframe is not None:
            self.dataframe = self._full_dataframe.copy()
            self._full_dataframe = None
            return True, "Selection canceled. All cases restored."
        return False, "No active selection to cancel."

    def delete_case(self, index):
        """Drops the case at the specified index."""
        if self.dataframe is not None and 0 <= index < len(self.dataframe):
            self.dataframe = self.dataframe.drop(index).reset_index(drop=True)
            return True
        return False

    def add_variable(self, name):
        """Adds a new empty column to the dataset."""
        if self.dataframe is None:
            self.dataframe = pd.DataFrame()
            
        if name in self.dataframe.columns:
            return False, "Variable already exists."
        
        self.dataframe[name] = np.nan
        return True, "Variable added."

    def delete_variable(self, name):
        """Removes a column from the dataset."""
        if self.dataframe is not None and name in self.dataframe.columns:
            self.dataframe.drop(columns=[name], inplace=True)
            return True, "Variable deleted."
        return False, "Variable not found."

    def new_from_expression(self, var_string):
        """Initializes a new empty dataset with columns parsed from a string."""
        cols = var_string.replace(',', ' ').split()
        if not cols:
            return False, "No variables provided."
            
        self.dataframe = pd.DataFrame(columns=cols)
        self._full_dataframe = None
        return True, "Dataset initialized."

    def calculate_set_coincidence(self, var1, var2, negate1=False, negate2=False):
        """
        Calculates the degree of overlap between two fuzzy sets (Coincidence).
        Formula: sum(min(X, Y)) / sum(max(X, Y))
        """
        if self.dataframe is None:
            return False, "Error: No data loaded."
            
        if var1 not in self.dataframe.columns or var2 not in self.dataframe.columns:
            return False, "Error: Variables not found."

        try:
            x = self.dataframe[var1].values
            y = self.dataframe[var2].values
            
            if negate1: x = 1 - x
            if negate2: y = 1 - y
            
            sum_min = np.sum(np.minimum(x, y))
            sum_max = np.sum(np.maximum(x, y))
            
            coincidence = sum_min / sum_max if sum_max > 0 else 0.0
            
            # Log action (PRD 009/010)
            self.logger.log_action(
                category="COINCIDENCE_ANALYSIS",
                description=f"Calculated set coincidence between '{var1}' and '{var2}'.",
                metadata={
                    "var1": var1,
                    "var2": var2,
                    "negate1": negate1,
                    "negate2": negate2,
                    "result": round(float(coincidence), 4)
                }
            )
            
            return True, coincidence
        except Exception as e:
            return False, f"Error calculating coincidence: {str(e)}"

