from delb import Document


def list_sets(base_url: str = 'https://oai.sbb.berlin/') -> bool:
    """
    queries an OAI-PMH service with the ``ListSets`` verb and expects
    a well-formed response with some actual sets in it.
    Boolean return value indicates success.

    >>> list_sets('http://edoc.hu-berlin.de/oai/request')
    True

    >>> list_sets('http://foo.bar')
    False

    """
    try:
        assert Document(f'{base_url}?verb=ListSets').xpath('//ListSets/set/setSpec')
    except BaseException:
        return False
    return True


def main():
    assert list_sets(), "ListSets failure"
