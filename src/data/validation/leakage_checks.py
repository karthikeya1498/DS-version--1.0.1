"""Checks for target leakage in feature tables."""
def find_leakage(feature_names, forbidden):
    return sorted(set(feature_names).intersection(forbidden))
