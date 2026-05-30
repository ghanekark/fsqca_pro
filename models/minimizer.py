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

    def minimize(self, minterms, dont_cares=[]):
        """
        Implements Quine-McCluskey minimization.
        minterms: list of binary strings (e.g. ['101', '111'])
        dont_cares: list of binary strings
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

        # Step 3: Filter out prime implicants that only cover don't cares
        # (Simplification: for QCA we usually just want the reduced terms covering the minterms)
        final_implicants = []
        for pi in prime_implicants:
            covers_minterm = False
            for mt in minterms:
                match = True
                for i in range(num_bits):
                    if pi[i] != '-' and pi[i] != mt[i]:
                        match = False
                        break
                if match:
                    covers_minterm = True
                    break
            if covers_minterm:
                final_implicants.append(pi)

        return sorted(final_implicants)
