from delb import Document


def list_sets(base_url: str = 'https://oai.sbb.berlin/') -> bool:
    """
    queries an OAI-PMH service with the ``ListSets`` verb and expects
    a ``resumptionToken`` in the response. Throws otherwise.

    >>> list_sets('https://www.ncbi.nlm.nih.gov/pmc/oai/oai.cgi')
    True

    """
    r = Document(f'{base_url}?verb=ListSets')
    assert r.xpath('//resumptionToken')
    return True

    
def main():
    list_sets()
