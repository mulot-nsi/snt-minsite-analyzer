import tinycss2


def get_selectors(content):
    selectors = []
    rules = tinycss2.parse_stylesheet(content, skip_comments=True, skip_whitespace=True)
    for rule in rules:
        selector = ''.join(token.serialize() for token in rule.prelude).strip()
        selectors.append(selector)

    return selectors
