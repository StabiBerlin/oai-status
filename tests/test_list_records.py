from urllib import parse

from oai_status.list_records import (
    get_resumption_token,
    list_records,
    main,
    request_list_records,
)


def test_request_list_records_resumption():
    doc = request_list_records(
        'illustrierte.liedflugschriften',
        resumption_token=(
            'metadataPrefix%3Doai_dc%26set%3Dillustrierte.liedflugschriften'
            '%26cursor%3D50%26batch_size%3D51'
        )
    )
    assert (resumption_token := get_resumption_token(doc))
    resumption_data = parse.parse_qs(parse.unquote(resumption_token))
    assert resumption_data == {
        'metadataPrefix': ['oai_dc'],
        'set': ['illustrierte.liedflugschriften'],
        'cursor': ['100'],
        'batch_size': ['51']
    }


def test_list_records_paging():
    assert len(list(list_records('reformation'))) == 73


def test_list_records_limited():
    assert len(list(list_records('reformation', limit=1))) == 1


def test_list_records_limited_paging():
    assert len(
        list(list_records('illustrierte.liedflugschriften', limit=75))
    ) == 75


def test_entrypoint():
    csv_data = main(
        ['', 'reformation'], 10
    )
    assert len(csv_data) == 10
    assert all(
        map(
            lambda row: row[0] < '1831',
            csv_data
        )
    )
