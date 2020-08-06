

def extract_alias(mapping, target_text):
    for key in mapping:
        match = [x for x in mapping[key] if x in target_text]
        if match and len(match) > 0:
            return key, match[0]
    return None, None
