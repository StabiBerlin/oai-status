from delb import Document


def list_sets():
    r = Document('https://oai.sbb.berlin/?verb=ListSets')
    assert r.xpath('//resumptionToken')

    
def main():
    list_sets()
