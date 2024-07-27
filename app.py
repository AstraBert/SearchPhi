import streamlit as st
from websearching import web_search
from llama_cpp_inf import run_inference_lcpp

def reply(query):
    jsonstr = web_search(query)
    results = run_inference_lcpp(jsonstr, query)
    return results

st.set_page_config(page_title="SearchPhi", page_icon="🔎")
# Title of the web app
st.title("SearchPhi🔎")
st.subheader("With llama.cpp!🦙")
# Input text box for the search query
query = st.text_input("Enter search term:")

# Number of results to display
num_results = st.number_input("Number of results to display:", min_value=1, max_value=5, value=3)

# Button to initiate search
if st.button("Search"):
    if query:
        results = reply(query)
        st.write(f"**Results for '{query}':**")
        st.write_stream(results)
    else:
        st.write("Please enter a search term.")