#!/usr/bin/env python
# coding: utf-8

# ## Search PubMed and ORCID for Single Author via Web Interface
#   - This is a web-based application
#       - Users can perform the task via a web browser
#       - No Python or Jupyter Notebook is required to be install
#   - Search from Pubmed and ORCID refereces by author
#   - PubMed provides a free API through NCBI's Entrez system, and the Biopython package offers a convenient interface
#   - Input: Author and ORCID
#   - Output: Publications

# ### Library

# In[1]:


import pandas as pd
from datetime import datetime
from Bio import Entrez, Medline
import requests

import warnings
warnings.filterwarnings('ignore')


# ### Create PubMed and ORCID search function

# In[2]:


def search_publications(author_name, orcid):
    
    ### Search PubMed for One Author
    
    # NCBI requests that users provide an email address
    Entrez.email = "wtuan@pennstatehealth.psu.edu"

    search_term = f'"{author_name}"[Author]'

    handle = Entrez.esearch(
        db="pubmed",
        term=search_term,
        retmax=100
    )

    record = Entrez.read(handle)
    pmids = record["IdList"]
    
    ### Retrieve Publication Information from PubMed

    handle = Entrez.efetch(
        db="pubmed",
        id=pmids,
        rettype="medline",
        retmode="text"
    )

    records = Medline.parse(handle)

    pubs = []

    for record in records:

        # Extract DOI from AID field
        doi = ""
    
        for aid in record.get("AID", []):
        
            if "[doi]" in aid.lower():
                doi = aid.replace(" [doi]", "").replace("[doi]", "")
                break
    
        pubs.append({
            "PMID": record.get("PMID", ""),
            "DOI": doi,
            "Title": record.get("TI", ""),
            "Journal": record.get("JT", ""),
            "Year": record.get("DP", "")[:4],
            "Authors": "; ".join(record.get("AU", [])),
            "Affiliations": "; ".join(record.get("AD", []))
                if isinstance(record.get("AD", []), list)
                else record.get("AD", "")
        })

    pubmed_df = pd.DataFrame(pubs)

    ### Retrieve Publications from ORCID
    
    url = f"https://pub.orcid.org/v3.0/{orcid}/works"

    headers = {
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)

    data = response.json()

    ### Extract Publication Information
 
    works = data.get("group", [])

    records = []

    for work in works:

        summary = work["work-summary"][0]

        title = summary.get("title", {}).get("title", {}).get("value", "")

        year = (
            summary.get("publication-date", {})
            .get("year", {})
            .get("value", "")
        )

        doi = ""
        pmid = ""

        ext_ids = summary.get("external-ids", {}).get("external-id", [])

        for ext in ext_ids:

            id_type = ext.get("external-id-type", "").lower()

            if id_type == "doi":
                doi = ext.get("external-id-value", "")

            elif id_type == "pmid":
                pmid = ext.get("external-id-value", "")
        
        records.append({
            "ORCID": orcid,
            "DOI": doi,
            "PMID": pmid,
            "Title": title,
            "Year": year
        })

    orcid_df = pd.DataFrame(records)
    
    ### Merge PubMed and ORCID
    
    pubmed_df["PubID"] = pubmed_df["DOI"].replace("", pd.NA)
    pubmed_df["PubID"] = pubmed_df["PubID"].fillna(pubmed_df["PMID"])

    orcid_df["PubID"] = orcid_df["DOI"].replace("", pd.NA)
    orcid_df["PubID"] = orcid_df["PubID"].fillna(orcid_df["PMID"])

    pubmed_df["PubID"] = pubmed_df["PubID"].astype("string").str.lower()
    orcid_df["PubID"] = orcid_df["PubID"].astype("string").str.lower()
   
    merged_df = pd.merge(
        pubmed_df,
        orcid_df,
        on="PubID",
        how="outer",
        indicator=True,
        suffixes=("_pubmed", "_orcid")
    )

    merged_df["Source"] = merged_df["_merge"].astype(str).map({
        "left_only": "pubmed_df",
        "right_only": "orcid_df",
        "both": "both"
    })

    merged_df.drop(columns="_merge", inplace=True)
    
    merged_df["PMID_pubmed"] = pd.to_numeric(
        merged_df["PMID_pubmed"],
        errors="coerce"
    )

    merged_df = merged_df.sort_values(
        by=["ORCID", "PMID_pubmed"],
        ascending=[True, True]
    ).reset_index(drop=True)
        
    return merged_df

