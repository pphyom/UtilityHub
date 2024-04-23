
def search_it(search_item: str, source2search: dict):
    """
    Recursively search the key in the dictionary. 

    """
    if hasattr(source2search, 'items'):
        for k, v in source2search.items():
            if k == search_item:
                yield v
            if isinstance(v, dict):     # check if the v is dictionary
                for result in search_it(search_item, v):
                    yield result
            elif isinstance(v, list):
                for x in v:
                    for result in search_it(search_item, x):
                        yield result


def search_pair(parent: str, child: str, source2search: dict):
    for k, v in source2search.items():
        if k == parent:
            pass