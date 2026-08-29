#!/usr/bin/env python
# coding: utf-8

# ## Search PubMed and ORCID for Single Author via Web Interface
#   - Create a Simple Web Interface
#   - This file's only job is:
#     1. Ask user for Author Name
#     2. Ask user for ORCID
#     3. Call your function
#     4. Show results

# ### Library

# In[ ]:


import pandas as pd
from io import BytesIO
from datetime import datetime
import streamlit as st
import re
from pubmed_search import search_publications

import warnings
warnings.filterwarnings('ignore')


# ### Call PubMed and ORCID search function via Web App

# In[ ]:


# Page Title
st.title("PubMed and ORCID Publication Extractor")

# User Input
author_name = st.text_input(
    "Author Name",
    placeholder="Tuan, WJ"
)

orcid = st.text_input(
    "ORCID",
    placeholder="0000-0003-3939-8979"
)

# Function to create Excel file in memory
def create_excel(df):

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    return output.getvalue()

# Search Button
if st.button("Search"):

    # Remove leading/trailing spaces
    author_name = author_name.strip()
    orcid = orcid.strip()

    # ORCID validation pattern
    orcid_pattern = r"^\d{4}-\d{4}-\d{4}-\d{4}$"

    # Input validation
    if not author_name and not orcid:

        st.error(
            "Please enter both Author Name and ORCID."
        )

    elif not author_name:

        st.error(
            "Please enter Author Name."
        )

    elif not orcid:

        st.error(
            "Please enter ORCID."
        )

    elif not re.match(orcid_pattern, orcid):

        st.error(
            "ORCID must be in the format: 0000-0000-0000-0000"
        )

    else:

        with st.spinner(
            "Searching PubMed and ORCID..."
        ):

            results = search_publications(
                author_name,
                orcid
            )

        st.success(
            f"Found {len(results)} publication records."
        )

        st.dataframe(
            results,
            use_container_width=True
        )

        # Create file name
        today = datetime.today().strftime("%Y%m%d")

        safe_author = (
            author_name.replace(", ", "_")
                       .replace(",", "_")
                       .replace(" ", "_")
        )

        filename = (
            f"publication_{safe_author}_{today}.xlsx"
        )

        # Create Excel file
        excel_data = create_excel(results)

        # Download button
        st.download_button(
            label="📥 Download Excel File",
            data=excel_data,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

