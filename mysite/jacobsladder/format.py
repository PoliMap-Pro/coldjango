from . import constants


def keep_query(return_format, election_result, query_set, model=None):
    if return_format == constants.TRANSACTION_FORMAT:
        if election_result and query_set:
            if model:
                if isinstance(query_set, dict):
                    query = model.objects.filter(**query_set).query
                else:
                    assert False
                    query = model.objects.all().query
            else:
                query = query_set.query
            election_result[constants.QUERIES].append(str(query))