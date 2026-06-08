class QCAMinimizer:
    def __init__(self):
        pass

    def _diff_by_one_bit(self, term1, term2):
        """Checks if two binary strings differ by exactly one bit."""
        diff_count = 0
        pos = -1
        for i in range(len(term1)):
            if term1[i] != term2[i]:
                diff_count += 1
                pos = i
        return diff_count == 1, pos

    def _covers(self, pi, minterm):
        """Returns True if the prime implicant (pi) covers the minterm."""
        for i in range(len(pi)):
            if pi[i] != '-' and pi[i] != minterm[i]:
                return False
        return True

    def minimize(self, minterms, dont_cares=[], tie_breaker_callback=None):
        """
        Implements Quine-McCluskey minimization.
        minterms: list of binary strings (e.g. ['101', '111'])
        dont_cares: list of binary strings
        tie_breaker_callback: optional callback to resolve tied PIs
        """
        if not minterms:
            return []

        all_terms = list(set(minterms + dont_cares))
        num_bits = len(all_terms[0])
        
        # Step 1: Group by number of 1s
        current_groups = {}
        for term in all_terms:
            ones = term.count('1')
            current_groups.setdefault(ones, set()).add(term)

        prime_implicants = set()
        
        # Step 2: Iterative merging
        while True:
            next_groups = {}
            merged = set()
            keys = sorted(current_groups.keys())
            
            for i in range(len(keys) - 1):
                group1 = current_groups[keys[i]]
                group2 = current_groups[keys[i+1]]
                
                for term1 in group1:
                    for term2 in group2:
                        match, pos = self._diff_by_one_bit(term1, term2)
                        if match:
                            new_term = term1[:pos] + '-' + term1[pos+1:]
                            ones = new_term.count('1')
                            next_groups.setdefault(ones, set()).add(new_term)
                            merged.add(term1)
                            merged.add(term2)
            
            # Identify prime implicants (terms that couldn't be merged)
            for group in current_groups.values():
                for term in group:
                    if term not in merged:
                        prime_implicants.add(term)
            
            if not next_groups:
                break
            current_groups = next_groups

        # Step 3: Prime Implicant Chart and Greedy Set Cover
        pi_pool = list(prime_implicants)
        
        # Build dictionary mapping minterms to covering PIs
        chart = {mt: [pi for pi in pi_pool if self._covers(pi, mt)] for mt in minterms}
        
        final_implicants = set()
        covered_minterms = set()

        # A. Find Essential Prime Implicants
        for mt, covering_pis in chart.items():
            if len(covering_pis) == 1:
                epi = covering_pis[0]
                final_implicants.add(epi)
                # Mark all minterms covered by this EPI
                for m in minterms:
                    if self._covers(epi, m):
                        covered_minterms.add(m)
                # Remove EPI from pool
                if epi in pi_pool:
                    pi_pool.remove(epi)

        # B. Greedy Set Cover for remaining uncovered minterms
        remaining_minterms = [mt for mt in minterms if mt not in covered_minterms]
        
        while len(covered_minterms) < len(minterms):
            max_newly_covered = 0
            tied_pis = []
            
            for pi in pi_pool:
                if pi in final_implicants:
                    continue
                
                # Count how many currently uncovered minterms this PI would cover
                count = sum(1 for mt in remaining_minterms if self._covers(pi, mt))
                
                if count > max_newly_covered:
                    max_newly_covered = count
                    tied_pis = [pi]
                elif count == max_newly_covered and count > 0:
                    tied_pis.append(pi)
            
            if not tied_pis:
                break
            
            # Resolve tie if needed
            if len(tied_pis) > 1 and tie_breaker_callback:
                selected_pis = tie_breaker_callback(tied_pis)
            else:
                selected_pis = tied_pis # Default: take all tied PIs (or the single best)

            for pi in selected_pis:
                final_implicants.add(pi)
                # Update covered_minterms
                newly_covered = [mt for mt in remaining_minterms if self._covers(pi, mt)]
                for mt in newly_covered:
                    covered_minterms.add(mt)
            
            # Update remaining pool and uncovered minterms
            for pi in tied_pis:
                if pi in pi_pool:
                    pi_pool.remove(pi)
            
            remaining_minterms = [mt for mt in remaining_minterms if mt not in covered_minterms]

        return sorted(list(final_implicants))
