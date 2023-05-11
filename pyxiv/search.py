# -*- coding: utf-8 -*-

from .eprint import ePrint
from .generate_eprint import eprint_from_atom_feed
from .helper_functions import convert_to_datetime, elapsed_time

from datetime import date, timedelta
from feedparser import parse
from os import stat
from time import time
from typing import Union


class Search:
    """
    Class for searching through e-prints submitted to arxiv.org using
    the [arXiv API](https://info.arxiv.org/help/api/index.html). Once
    e-prints are found that match the search criteria, they can be
    downloaded locally as .pdf files.

    Parameters
    ----------
    query : str
        The core part of a query compatible with the arXiv API.
        Instructions on how to construct queries are available
        [here](https://info.arxiv.org/help/api/user-manual.html#query_details).
        `query` should be formatted as `'au:del_maestro+AND+ti:checkerboard'`,
        for example. Note that the prefix '`query?search_query=`'
        is *not* included; this is handled automatically by the
        `Search` class. As well, subsequent query specifications like
        `'&start=0&max_results=1'` are handled by other arguments of
        `Search`. See `keyword_query` and `author_query` for pre-set
        query types.
    start_date : str
        The earliest possible submission date for an e-print included
        in the search results (i.e. e-prints submitted prior to
        `start_date` are excluded). One of `'today'`, `'yesterday'`,
        or an ISO-formatted (`'YYYY-MM-DD'`) string. Note that
        submission date is not a search field available to the arXiv
        API; filtering by start date is therefore post-processing that
        occurs after the API has been queried.
    end_date : str, default 'today'
        The latest possible submission date for an e-print included
        in the search results (i.e. e-prints submitted after
        `start_date` are excluded). One of `'today'`, `'yesterday'`,
        or an ISO-formatted (`'YYYY-MM-DD'`) string. Note that
        submission date is not a search field available to the arXiv
        API; filtering by end date is therefore post-processing that
        occurs after the API has been queried.
    max_results : int, default 250
        The number of e-prints returned by the query of the arXiv API.
        Note that since filtering by date occurs post-query, the value
        of `max_results` will typically not correspond to the number
        of e-prints listed in the search results given by this class.
    sort_order : str, default 'descending'
        The sort order used by the query of the arXiv API. If set to
        'descending', it sorts from newest e-prints to oldest; if set
        to 'ascending' it sorts from oldest e-prints to newest.
    """
    def __init__(self, query: str, start_date: str, end_date: str = "today",
                 max_results: int = 250, sort_order: str = "descending") -> None:
        self.query       = query
        self.start_date  = start_date
        self.end_date    = end_date
        self.max_results = max_results
        self.sort_order  = sort_order

        self.__search_results = self.__search_eprints()

    def __str__(self) -> str:
        print_string  = "Search("
        print_string += f"query='{self.query}', "
        print_string += f"start_date='{self.start_date}', "
        print_string += f"end_date='{self.end_date}', "
        print_string += f"max_results={self.max_results}, "
        print_string += f"sort_order={self.sort_order})"
        return print_string
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Search):
            param_match  = self.query == other.query
            param_match &= self.start_date == other.start_date
            param_match &= self.end_date == other.end_date
            param_match &= self.max_results == other.max_results
            param_match &= self.sort_order == other.sort_order
            return param_match
        else:
            return False

    def __process_query(self) -> str:
        """
        Method that ensures the input for `query` is valid, then
        replaces any spaces in `query` with `'+'` to make `query`
        compatible with the arXiv API.
        """
        if not isinstance(self.query, str):
            raise ValueError("invalid input for `query`, expected str.")
        
        # Replace any spaces with + for URL compatibility
        query = self.query.replace(" ", "+")

        return query
    
    def __process_dates(self) -> tuple[date]:
        """
        Method that ensures the inputs for `start_date` and `end_date`
        are valid, then creates corresponding datetime.date objects.
        """
        start_date = convert_to_datetime(self.start_date, "start_date")
        end_date   = convert_to_datetime(self.end_date,   "end_date")

        if start_date > end_date:
            raise ValueError("invalid input for `start_date`, "
                             "expected a date before `end_date`.")
        
        if end_date > date.today():
            raise ValueError("invalid input for `end_date`, "
                             "cannot be a date in the future.")
        
        yesterday = date.today() - timedelta(days=1)
        if start_date < yesterday:
            print("Note: a value of `start_date` earlier than yesterday has "
                  "been used. It may be necessary to increase `max_results` "
                  "to ensure the query searches sufficiently far back in time. "
                  "The maximum permitted value of `max_results` is 30,000.")
            
        return start_date, end_date
    
    def __process_max_results(self) -> int:
        """
        Method that ensures the input for `max_results` is valid.
        """
        max_results = self.max_results
        if (not isinstance(max_results, int)) or (max_results <= 0):
            raise ValueError("invalid input for `max_results`, "
                             "expected int greater than 0.")
        return max_results
        
    def __process_sort_order(self) -> str:
        """
        Method that ensures the input for `sort_order` is valid.
        """
        sort_order = self.sort_order.lower()
        permitted_orders = ("ascending", "descending")
        if sort_order not in permitted_orders:
            raise ValueError("invalid input for `sort_order`, "
                             "expected 'ascending' or 'descending'.")
        if sort_order == "ascending":
            print("Note: `sort_order` has been set to 'ascending', which "
                  "searches from oldest e-prints to newest. This is only "
                  "recommended when searching for very old e-prints.")
        return sort_order
            
    def __search_eprints(self) -> list[ePrint]:
        """
        Method that queries the arXiv API, selects all e-prints from
        the query results that were submitted between `start_date` and
        `end_date`, and returns the remaining e-prints as a list of
        `ePrint` objects sorted from oldest to newest.
        """
        # Validate inputs to ensure compatibility with arXiv API
        query                = self.__process_query()
        start_date, end_date = self.__process_dates()
        max_results          = self.__process_max_results()
        sort_order           = self.__process_sort_order()

        # Construct URL for arXiv API query
        base_url   = "http://export.arxiv.org/api/"
        query      = f"search_query={query}"
        query_max  = f"start=0&max_results={max_results}"
        query_sort = f"sortBy=submittedDate&sortOrder={sort_order}"
        query_url  = f"query?{query}&{query_max}&{query_sort}"
        url        = base_url + query_url

        t0 = time()
        print("Acquiring query results from the arXiv API...")

        query_results = parse(url)

        # Filter results by date
        eprints = []
        for atom_feed in query_results.entries:
            eprint = eprint_from_atom_feed(atom_feed)

            if eprint.date_submitted > end_date:
                continue
            elif eprint.date_submitted < start_date:
                break

            eprints.append(eprint)

        query_time = time() - t0
        print(f"Results acquired in {elapsed_time(query_time)}.")

        return eprints[::-1]

    def __no_results(self) -> None:
        """
        Method that prints a message to help with troubleshooting if no
        e-prints are returned by `__search_eprints`.
        """
        print("No e-prints have been found matching the given query during the "
              "provided dates. Please ensure that:")
        print("1. The query is formatted correctly (see "
              "https://info.arxiv.org/help/api/user-manual.html#query_details).")
        print("2. The provided dates are correct.")
        print("3. The value of `max_results` is large enough to reach the "
              "provided dates.")
    
    def results(self, detail: str = "low") -> Union[str, None]:
        """
        Method that generates a string containing the results of
        the search.

        Parameters
        ----------
        detail : str, default 'low'
            Controls the level of detail included in the summary of
            each `ePrint` object. If set to `'high'`, all relevant
            fields are included. If set to `'low'`, `abstract`,
            `comment`, `all_categories`, `doi`, `journal_ref`, and
            `date_updated` are omitted.

        Returns
        -------
        Union[str, None]
            If the search yields results, a string that
            concatenates `ePrint.summary(detail=detail)` for each
            e-print is returned. If the search yields no results,
            `None` is returned and a message to help with
            troubleshooting is printed.
        """
        # Get e-prints
        eprints   = self.__search_results
        N_eprints = len(eprints)

        # List e-prints
        if N_eprints > 0:
            sing_or_plur = "result" if N_eprints == 1 else "results"
            print(f"The specified query yielded {N_eprints} {sing_or_plur}:")
            results_string = ""
            for i, eprint in enumerate(eprints):
                results_string += eprint.summary(detail=detail)
                # Add line skip to each non-final summary
                if i != N_eprints - 1:
                    results_string += "\n\n"
            return results_string
        
        # Troubleshooting suggestions if no e-prints found
        else:
            self.__no_results()

    def download_results(self, save_directory: str) -> Union[list[str], None]:
        """
        Method that downloads the search results as .pdf files to a
        specified local directory.

        Parameters
        ----------
        save_directory : str
            The directory to which the e-prints are saved.

        Returns
        -------
        Union[list[str], None]
            If the search yields results, a list of the names of the
            downloaded files is returned. If the search yields no results,
            `None` is returned and a message to help with
            troubleshooting is printed.
        """
        # Get e-prints
        eprints   = self.__search_results
        N_eprints = len(eprints)

        # Download e-prints
        if N_eprints > 0:

            # Formatting for loop statements
            padding = len(str(N_eprints))
            indices = [str(i).rjust(padding) for i in range(1, N_eprints + 1)]

            # Loop over query results and download each e-print
            t0            = time()
            file_names    = []
            download_size = 0.0

            print("Downloading e-prints...")
            for i, eprint in enumerate(eprints):
                print(f"[{indices[i]}/{N_eprints}] '{eprint.title}' "
                      f"({eprint.arxiv_id})")
                file_name = eprint.download(save_directory, show_status=False)
                file_names.append(file_name)
                download_size += stat(file_name).st_size

            download_time = time() - t0
            download_size /= 1024**2

            # Print download summary message
            sing_or_plur = "e-print" if N_eprints == 1 else "e-prints"
            print(f"Download complete! {N_eprints} {sing_or_plur} "
                  f"({download_size:.1f} MiB) were downloaded in "
                  f"{elapsed_time(download_time)} and saved to "
                  f"{save_directory}.")
            
            return file_names

        # Troubleshooting suggestions if no e-prints found
        else:
            self.__no_results()
