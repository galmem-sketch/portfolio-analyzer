def to_float(val):
    if hasattr(val, 'iloc'):
        return float(val.iloc[0])
    return float(val)
