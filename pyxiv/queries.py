# -*- coding: utf-8 -*-

"""
Pre-set query types to simplify the process of constructing valid
queries for the arXiv API.
"""

def keyword_query(keywords: list[str], field_type: str = "all",
                  logical: str = "OR") -> str:
    """
    Generates a query for the arXiv API based off a list of keywords,
    the field in which to search for those keywords, and the boolean
    value used to join the keywords in the query.

    Parameters
    ----------
    keywords : list[str]
        A list of keywords to search for in the arXiv API.
    field_type : str, default 'all'
        The field in which to search for the keywords in `keywords`.
        Options are `'ti'` (title), `'au'` (author), `'abs'`
        (abstract), `'co'` (comment), `'jr'` (journal reference),
        `'cat'` (category), `'rn'` (report number), `'id'` (ID),
        and `'all'` (all of the above).
    logical : str, default 'OR'
        The boolean value used to join the keywords in `keywords`.
        Options are `'AND'`, `'OR'`, and `'ANDNOT'`.

    Returns
    -------
    str
        A query based on the provided keywords that is compatible with
        the arXiv API.
    """
    # Validate keywords input
    is_list   = isinstance(keywords, list)
    is_string = all(isinstance(word, str) for word in keywords)
    if (not is_list)  or (not is_string):
        raise ValueError("invalid input for `keywords`, "
                         "expected list of str.")
    
    # Validate field_type input
    permitted_field_types = ("ti", "au", "abs", "co", "jr", "cat",
                             "rn", "id", "all")
    if field_type not in permitted_field_types:
        raise ValueError("invalid input for `field_type`, expected 'ti', "
                         "'au', 'abs', 'co', 'jr', 'cat', 'rn', 'id', or "
                         "'all'.")
    
    # Validate logical input
    permitted_logicals = ("AND", "OR", "NOTAND")
    if logical not in permitted_logicals:
        raise ValueError("invalid input for `logical`, expected 'AND', "
                         "'OR', or 'NOTAND'")

    # Generate query string
    query = f"+{logical}+".join(f"{field_type}:{keyword}"
                                for keyword in keywords)

    return query


def author_query(first_name: str, last_name: str, category: str = "") -> str:
    """
    Generates a query for the arXiv API based off the first and last
    name of an author, as well as the category in which to search.
    
    Parameters
    ----------
    first_name : str
        The first name of the author.
    last_name : str
        The last name of the author.
    category : str, default ''
        The category in which to search (e.g. astro-ph.EP). If set to
        '', the query searches through all categories. For the complete
        list of categories, see https://arxiv.org/category_taxonomy.

    Returns
    -------
    str
        A query based on the provided first name, last name, and
        category that is compatible with the arXiv API.
    """
    query = f"au:{first_name}+AND+au:{last_name}"
    if category:
        query += f"+AND+cat:{category}"
    return query
