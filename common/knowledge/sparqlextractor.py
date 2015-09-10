import logging
from django.utils import timezone

from pyelasticsearch import ElasticSearch, BulkError, IndexAlreadyExistsError, bulk_chunks
from SPARQLWrapper import SPARQLWrapper, JSON, GET
from common.knowledge.provider import Provider
from abc import abstractmethod
from urlparse import urlparse


class SparqlExtractor(Provider):

    STEP_SIZE = 1000

    @abstractmethod
    def query(self):
        raise NotImplementedError('No query provided')

    @abstractmethod
    def prefixes(self):
        raise NotImplementedError('No prefixes provided')

    @classmethod
    def query_append_offset_limit(cls):
        return '{}\nOFFSET {} LIMIT {}'

    @classmethod
    def query_count_instances(cls):
        return 'SELECT (COUNT(?s) AS ?count) {{ ?s a <{}> }}'

    @classmethod
    def endpoint_to_index(cls, endpoint):
        url = urlparse(endpoint)
        return url.hostname

    @classmethod
    def instantiate_sparql(cls, endpoint):
        sparql = SPARQLWrapper(endpoint)
        sparql.method = GET
        sparql.setReturnFormat(JSON)
        return sparql

    def prepare_index(self, es, concept):
        index_name = self.endpoint_to_index(concept.endpoint)
        try:
            # create the document index
            es.create_index(index_name)
        except IndexAlreadyExistsError:
            pass

        try:
            # clear all items of type in document
            es.delete_all(index_name, concept.id)
        except Exception as e:
            print(e)

        return index_name

    @classmethod
    def get_instance_count(cls, concept, sparql=None):
        if sparql is None:
            SparqlExtractor.instantiate_sparql(concept.endpoint)
        sparql.setQuery(SparqlExtractor.query_count_instances().format(concept.linked_type))
        return long(sparql.queryAndConvert()['results']['bindings'][0]['count']['value'])

    @classmethod
    def extract_range(cls, query, offset, sparql, step_size=STEP_SIZE):
        data = []
        sparql.setQuery(SparqlExtractor.query_append_offset_limit().format(query, offset, step_size))
        results = sparql.query().convert()
        #print(SparqlExtractor.query_append_offset_limit().format(query, offset, step_size))
        # process result set
        if len(results["results"]["bindings"]) > 0:
            # transform result set
            for result in results["results"]["bindings"]:
                item = {}
                for key in result:
                    item[key] = result[key]['value']
                data.append(item)
        return data

    def dump(self, types):
        # establish connection to ElasticSearch
        es = ElasticSearch(self.elastic_search_url)
        # prepare index
        index = self.prepare_index(es, types)

        # instantiate SPARQLWrapper
        sparql = self.instantiate_sparql(types.endpoint)

        if types.custom_query is not None:
            query = self.prefixes() + types.custom_query
        else:
            query = self.prefixes() + self.query().format(types.linked_type)

        count = self.get_instance_count(types, sparql=sparql)

        for i in xrange(0, count, SparqlExtractor.STEP_SIZE):
            data = self.extract_range(query, i, sparql, step_size=SparqlExtractor.STEP_SIZE)
            if len(data) > 0:
                # create generator
                def items():
                    for item in data:
                        yield es.index_op(item)

                for chunk in bulk_chunks(items(), docs_per_chunk=500, bytes_per_chunk=10000):
                    try:
                        # import data in elastic search
                        es.bulk(chunk, doc_type=types.id, index=index)
                    except BulkError as e:
                        print (e)

        # refresh the index
        es.refresh(index)

        # update retrieved date
        types.retrieved_at = timezone.now()
        types.save()
