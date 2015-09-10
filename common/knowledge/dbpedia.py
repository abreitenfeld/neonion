from common.knowledge.sparqlextractor import SparqlExtractor


class DBpedia(SparqlExtractor):

    def __init__(self, elastic_search_url):
        self.elastic_search_url = elastic_search_url

    def prefixes(self):
        return 'PREFIX dbo: <http://dbpedia.org/ontology/>\n' \
               'PREFIX res: <http://dbpedia.org/resource/>\n' \
               'PREFIX dbp: <http://dbpedia.org/property/>\n'

    def query(self):
        return 'SELECT DISTINCT * WHERE {{' \
            ' ?uri a <{}> .' \
            ' ?uri rdfs:label ?label' \
            ' OPTIONAL {{ ?uri dbo:abstract ?description FILTER (lang(?description) = "en") }}' \
            ' FILTER (lang(?label) = "en")' \
            '}}'
