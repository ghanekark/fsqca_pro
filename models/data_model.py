import pandas as pd
import numpy as np
import os
import itertools
import re
from models.minimizer import QCAMinimizer

class QCADataModel:
    def __init__(self):
        self.dataframe = None
        self.truth_table_df = None

    def load_file(self, filepath):
        """
        Reads .csv and tab-delimited .dat files into a pandas DataFrame.
        Applies dynamic sanitization and ensures complete-case analysis.
        Returns a tuple (success: bool, message: str)
        """
        if not os.path.exists(filepath):
            return False, f"Error: File '{filepath}' does not exist."

        _, ext = os.path.splitext(filepath)
        try:
            if ext.lower() == '.csv':
                df = pd.read_csv(filepath)
            elif ext.lower() == '.dat':
                df = pd.read_csv(filepath, sep='\t')
            else:
                return False, f"Error: Unsupported file extension '{ext}'."
            
            initial_rows = len(df)
            
            # 1. Clean column names (spaces -> _, remove non-alphanumeric)
            new_columns = []
            for col in df.columns:
                clean_name = str(col).replace(' ', '_')
                clean_name = re.sub(r'[^a-zA-Z0-9_]', '', clean_name)
                new_columns.append(clean_name)
            df.columns = new_columns
            
            # 2. Dynamic numeric conversion
            # Iterate through all columns. If conversion to numeric preserves > 50% of 
            # original non-null values, replace with numeric version. Otherwise leave as is.
            for col in df.columns:
                orig_count = df[col].count()
                if orig_count == 0:
                    continue
                
                temp_numeric = pd.to_numeric(df[col], errors='coerce')
                new_count = temp_numeric.count()
                
                if (new_count / orig_count) > 0.5:
                    df[col] = temp_numeric
            
            # 3. Complete-case analysis (drop rows with any NaNs in the final dataframe)
            df.dropna(inplace=True)
            self.dataframe = df
            
            final_rows = len(self.dataframe)
            dropped_rows = initial_rows - final_rows
            
            success_msg = f"Successfully loaded {filepath}. Total cases: {final_rows}."
            if dropped_rows > 0:
                success_msg += f" (Note: {dropped_rows} rows were dropped due to missing or invalid data)."
            
            return True, success_msg
        except Exception as e:
            return False, f"Error loading file: {str(e)}"

    def save_file(self, dataframe, filepath):
        """
        Saves a pandas DataFrame to a file. 
        Supports .csv and .dat (tab-delimited).
        Returns a tuple (success: bool, message: str)
        """
        _, ext = os.path.splitext(filepath)
        try:
            if ext.lower() == '.csv':
                dataframe.to_csv(filepath, index=False)
            elif ext.lower() == '.dat':
                dataframe.to_csv(filepath, sep='\t', index=False)
            else:
                return False, f"Error: Unsupported file extension '{ext}' for saving."
            
            return True, f"Successfully saved to {filepath}"
        except Exception as e:
            return False, f"Error saving file: {str(e)}"

    def calibrate_variable(self, source_col, new_col, p_full, p_cross, p_non):
        """
        Calculates fuzzy membership scores using the fsQCA log-odds method.
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
            
            return True, f"Successfully calibrated '{source_col}' into '{new_col}'"
        except Exception as e:
            return False, f"Error during calibration: {str(e)}"

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

    def generate_truth_table(self, conditions, outcome):
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
                success, _ = self.calibrate_variable(col, f"f_{col}", p_full, p_cross, p_non)
                if success:
                    count += 1
                    
        return True, f"Successfully auto-calibrated {count} numeric variables."


    def run_standard_analysis(self, truth_table_df, freq_thresh, consist_thresh, assumptions_dict=None):
        """
        Executes standard QCA minimization (Complex, Parsimonious, and Intermediate solutions).
        Uses the provided truth_table_df which should include 'outcome_code'.
        """
        df = truth_table_df
        
        # Identify non-condition columns
        condition_cols = [c for c in df.columns if c not in ['frequency', '_raw_freq', 'raw_consistency', 'outcome_code', 'pri_consist', 'sym_consist', 'cases']]
        
        # 1. Identify positive minterms
        # outcome_code '1' is forced positive.
        # outcome_code '' uses thresholds.
        pos_mask = (df['outcome_code'] == '1') | \
                   ((df['outcome_code'] == '') & (df['_raw_freq'] >= freq_thresh) & (df['raw_consistency'] >= consist_thresh))
        positive_df = df[pos_mask]
        
        # 2. Identify remainder minterms
        # outcome_code '-' is forced remainder.
        # outcome_code '' and frequency < threshold is remainder.
        rem_mask = (df['outcome_code'] == '-') | \
                   ((df['outcome_code'] == '') & (df['_raw_freq'] < freq_thresh))
        remainder_df = df[rem_mask]
        
        # 3. Convert binary configurations to strings
        def df_to_bitstrings(df_subset, cols):
            bitstrings = []
            for row in df_subset.itertuples(index=False):
                # We use getattr to safely get values by name.
                s = "".join(str(int(getattr(row, c))) for c in cols)
                bitstrings.append(s)
            return bitstrings

        pos_minterms = df_to_bitstrings(positive_df, condition_cols)
        rem_minterms = df_to_bitstrings(remainder_df, condition_cols)
        
        if len(pos_minterms) == 0:
            raise ValueError("Error: No configurations passed the frequency and consistency thresholds (The 1-Matrix is empty). Try lowering your thresholds.")
        
        # 4. Filter easy counterfactuals for intermediate solution
        easy_minterms = []
        if assumptions_dict:
            for rem in rem_minterms:
                is_easy = True
                for i, cond in enumerate(condition_cols):
                    assumption = assumptions_dict.get(cond, "Present or Absent")
                    if assumption == "Present" and rem[i] == '0':
                        is_easy = False
                        break
                    elif assumption == "Absent" and rem[i] == '1':
                        is_easy = False
                        break
                if is_easy:
                    easy_minterms.append(rem)
        
        # 5. Instantiate minimizer
        minimizer = QCAMinimizer()
        
        # 6. Complex Solution (No remainders)
        complex_sol = minimizer.minimize(pos_minterms, [])
        
        # 7. Parsimonious Solution (All remainders as don't cares)
        parsimonious_sol = minimizer.minimize(pos_minterms, rem_minterms)

        # 8. Intermediate Solution (Only easy remainders as don't cares)
        intermediate_sol = minimizer.minimize(pos_minterms, easy_minterms)
        
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

    def calculate_necessary_conditions(self, conditions, outcome):
        """
        Calculates necessity consistency and coverage for each condition and its negation.
        """
        if self.dataframe is None:
            return None
            
        outcome_data = self.dataframe[outcome].values
        sum_outcome = np.sum(outcome_data)
        
        if sum_outcome == 0:
            return None
            
        results = []
        
        for cond in conditions:
            cond_data = self.dataframe[cond].values
            
            # Positive condition
            consist = np.sum(np.minimum(cond_data, outcome_data)) / sum_outcome
            sum_cond = np.sum(cond_data)
            cover = np.sum(np.minimum(cond_data, outcome_data)) / sum_cond if sum_cond > 0 else 0.0
            
            results.append({
                'Condition': cond,
                'Consistency': consist,
                'Coverage': cover
            })
            
            # Negated condition
            neg_cond_data = 1 - cond_data
            neg_consist = np.sum(np.minimum(neg_cond_data, outcome_data)) / sum_outcome
            sum_neg_cond = np.sum(neg_cond_data)
            neg_cover = np.sum(np.minimum(neg_cond_data, outcome_data)) / sum_neg_cond if sum_neg_cond > 0 else 0.0
            
            results.append({
                'Condition': f"~{cond}",
                'Consistency': neg_consist,
                'Coverage': neg_cover
            })
            
        df_res = pd.DataFrame(results)
        return df_res.sort_values(by='Consistency', ascending=False)

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
