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
from pubmed_search import search_publications

import warnings
warnings.filterwarnings('ignore')


# ### Call PubMed and ORCID search function via Web App

# In[ ]:


st.title("PubMed and ORCID Publication Extractor")

author_name = st.text_input(
    "Author Name"
)

orcid = st.text_input(
    "ORCID"
)

# Function to create Excel file in memory
def create_excel(df):

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    return output.getvalue()


if st.button("Search"):

    results = search_publications(
        author_name,
        orcid
    )

    st.dataframe(results)

    # Create filename
    today = datetime.today().strftime("%Y%m%d")

    safe_author = (
        author_name.replace(", ", "_")
                   .replace(",", "_")
                   .replace(" ", "_")
    )

    filename = f"publication_{safe_author}_{today}.xlsx"

    # Create Excel file
    excel_data = create_excel(results)

    # Download button
    st.download_button(
        label="📥 Download Excel File",
        data=excel_data,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

