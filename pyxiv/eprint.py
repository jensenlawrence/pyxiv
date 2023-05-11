# -*- coding: utf-8 -*-

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from requests import get
from shutil import copyfileobj
from typing import Union


@dataclass(frozen=True)
class ePrint:
    """
    Class for storing the data associated with an e-print available on
    arxiv.org. This class is not intended for manual use (i.e. the
    values of the class arguments should be obtained *only* from a
    query of the arXiv API and not specified by hand).

    Parameters
    ----------
    title : str
        The title of the arXiv e-print.
    authors : list[str]
        The author(s) of the arXiv e-print.
    abstract : str
        The abstract of the arXiv e-print.
    comment : Union[str, None]
        Any comments associated with the arXiv e-print.
        Note: not all e-prints have associated comments. In this case,
        it is recommended to set `comment` to `None`.
    primary_category : str
        The primary category associated with the arXiv e-print
        (e.g. astro-ph.EP).
    all_categories : list[str]
        All categories associated with the arXiv e-print.
    arxiv_id : str
        The arXiv ID of the arXiv e-print.
    abs_url : str
        The URL of the abstract of the arXiv e-print.
    pdf_url : str
        The URL of the .pdf of the arXiv e-print.
    doi : Union[str, None]
        The DOI of the publication associated with the arXiv e-print.
        Note: not all e-prints are associated with a publication that
        has a DOI. In this case, it is recommended to set `doi` to
        `None`.
    doi_url : Union[str, None]
        The DOI URL of the publication associated with the arXiv
        e-print. Note: not all e-prints are associated with a
        publication that has a DOI. In this case, it is recommended to
        set `doi_url` to `None`.
    journal_ref : Union[str, None]
        The journal reference of the publication associated with the
        arXiv e-print. Note: not all e-prints are associated with a 
        publication. In this case, it is recommended to set
        `journal_ref` to `None`.
    date_submitted : datetime.date
        The date the arXiv e-print was submitted. Note that the date an
        e-print was submitted does not necessarily correspond to the
        date it became available to the public.
    date_updated : datetime.date
        The date the arXiv e-print was last updated.
    """
    title: str
    authors: list[str]
    abstract: str
    comment: Union[str, None]
    primary_category: str
    all_categories: list[str]
    arxiv_id: str
    abs_url: str
    pdf_url: str
    doi: Union[str, None]
    doi_url: Union[str, None]
    journal_ref: Union[str, None]
    date_submitted: date
    date_updated: date

    def summary(self, detail: str = "low") -> str:
        """
        Method that generates a summary of the data associated with the
        arXiv e-print represented by the given instance of `ePrint`.
        Two levels of detail are possible: `'low'` and `'high'`.

        Parameters
        ----------
        detail : str, default 'low'
            Controls the level of detail included in the summary. If
            set to `'high'`, all relevant fields are included. If set
            to `'low'`, `abstract`, `comment`, `all_categories`, `doi`,
            `journal_ref`, and `date_updated` are omitted.

        Returns
        -------
        str
            Summary of the data associated with the arXiv e-print.
        """
        # Validate detail input
        if detail not in ("low", "high"):
            raise ValueError("invalid input for `detail`, "
                             "expected 'low' or 'high'.")
        
        # All components of summary
        summary_components = (
            "-"*40 + "\n",
            f"arXiv.org e-Print {self.arxiv_id}\n",
            "-"*40 + "\n",
            f"Title: {self.title}\n",
            f"Author(s): {', '.join(self.authors)}\n",
            f"Abstract: {self.abstract}\n",
            f"Comment: {self.comment}\n",
            f"Primary category: {self.primary_category}\n",
            f"All categories: {', '.join(self.all_categories)}\n",
            f"URL: {self.pdf_url}\n",
            f"DOI: {self.doi_url}\n",
            f"Journal reference: {self.journal_ref}\n",
            f"Submitted: {self.date_submitted}",
            "\n",
            f"Last updated: {self.date_updated}"
        )

        summary_string = ""

        # Low-detail summary omits abstract, comment, all categories, DOI,
        # journal reference, and last updated
        if detail == "low":
            for i in (0, 1, 2, 3, 4, 7, 9, 12):
                summary_string += summary_components[i]

        # High-detail summary includes all summary components
        else:
            for component in summary_components:
                summary_string += component 

        return summary_string

    def download(self, save_directory: str, show_status: bool = True) -> str:
        """
        Method that downloads a .pdf file of the arXiv e-print
        represented by the given instance of `ePrint`.

        Parameters
        ----------
        save_directory : str
            The directory to which the e-print will be saved.
        show_status : bool, default True
            Controls whether download status messages are printed.
            Messages are printed when `True` and not printed otherwise.

        Returns
        -------
        str
            The path to the downloaded arXiv e-print.
        """
        # Validate show_status input
        if show_status not in (True, False):
            raise ValueError("invalid input for `show_status`, "
                             "expected True or False.")

        # Create save directory if it does not exist
        path = Path(save_directory)
        path.mkdir(parents=True, exist_ok=True)

        # Combine save directory and arXiv ID to create file name
        file_name = f"{save_directory}/{self.arxiv_id}.pdf"

        if show_status:
            print(f"Downloading '{self.title}' ({self.arxiv_id})...")

        # Save .pdf content from URL to local file
        response = get(self.pdf_url, stream=True)
        with open(file_name, "wb") as eprint_pdf:
            copyfileobj(response.raw, eprint_pdf)

        if show_status:
            print(f"Download complete! e-Print saved as {file_name}.")

        return file_name
