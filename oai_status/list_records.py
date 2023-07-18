import sys
from typing import Iterable

from delb import Document, TagNode


def request_list_records(
    setSpec: str, metadata_prefix: str = 'oai_dc', resumption_token: str = None
) -> Document:
    src = 'https://oai.sbb.berlin/?verb=ListRecords'
    if resumption_token:
        src += f'&resumptionToken={resumption_token}'
    else:
        src += f'&metadataPrefix={metadata_prefix}&set={setSpec}'
    return Document(src)


def get_records(doc: Document) -> Iterable[TagNode]:
    records = doc.xpath('//ListRecords/record')
    yield from records


def get_resumption_token(doc: Document) -> str:
    '''
    >>> get_resumption_token(request_list_records('illustrierte.liedflugschriften'))
    'metadataPrefix%3Doai_dc%26set%3Dillustrierte.liedflugschriften%26cursor%3D50%26batch_size%3D51'

    '''
    token_node = doc.xpath('//resumptionToken').first
    if token_node:
        return token_node.full_text
    return None


def extract_dc_bibl_data(record: TagNode, *fields: list[str]) -> list[str]:
    '''
    extract bibliographic data from the dublin core namespace of an OAI-PMH record element.

    >>> tagnode = Document(
    ...     '<record><metadata><oai_dc:dc '
    ...     'xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" '
    ...     'xmlns:dc="http://purl.org/dc/elements/1.1/">'
    ...     '<dc:publisher>Gutknecht, Friedrich</dc:publisher>'
    ...     '<dc:creator>Böschenstein, Johann</dc:creator></oai_dc:dc></metadata></record>'
    ... ).root

    >>> extract_dc_bibl_data(tagnode, 'creator', 'publisher', 'date')
    ['Böschenstein, Johann', 'Gutknecht, Friedrich', '']

    '''
    def matching_nodes(field: str) -> list[TagNode]:
        return list(record.iterate_descendants(
            lambda descendant: (
                isinstance(descendant, TagNode) and descendant.universal_name.endswith(field)
            )
        ))
    return [
        matches[0].full_text if matches else ''
        for matches in map(matching_nodes, fields)
    ]


def list_records(
    setSpec: str, metadata_prefix: str = 'oai_dc', limit: int = -1
) -> Iterable[TagNode]:
    '''
    retrieve records of a certain set from OAI endpoint, i.e. make requests with the `ListRecords`
    verb.
    '''
    counter = type('counter', (), dict(left=limit))()

    def yield_records(doc: Document) -> Iterable[TagNode]:
        for record in get_records(doc):
            if not counter.left:
                return
            yield record
            counter.left -= 1

    doc = request_list_records(setSpec, metadata_prefix)
    yield from yield_records(doc)
    if not counter.left:
        return

    while resumption_token := get_resumption_token(doc):
        doc = request_list_records(setSpec, metadata_prefix, resumption_token)
        yield from yield_records(doc)
        if not counter.left:
            return


def main(argv: list[str] = sys.argv, limit: int = -1):
    setSpec = argv[-1] if len(argv) > 1 else 'illustrierte.liedflugschriften'
    results = []
    for row in map(
        lambda record: extract_dc_bibl_data(record, 'date', 'publisher', 'coverage', 'creator'),
        list_records(setSpec, limit=limit)
    ):
        print(', '.join(row))
        results += [row]
    if 'unittest' in sys.modules:
        return results
