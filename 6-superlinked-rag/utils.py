from superlinked.framework.dsl.query.result import Result


def present_result(result: Result):
    """A small helper function to present our query results"""
    
    df = result.to_pandas()
    
    return df
