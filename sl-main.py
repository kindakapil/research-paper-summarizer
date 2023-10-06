import streamlit as st
import PyPDF2
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest
import tempfile
import os

# Function to extract abstract from a PDF file
def extract_abstract_from_pdf(pdf_path):
    abstract = ""
    with open(pdf_path, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            if "abstract" in page_text.lower():
                abstract_start_idx = page_text.lower().find("abstract")
                abstract = page_text[abstract_start_idx:]
                break
    return abstract

# Function to summarize text
def summarize_text(text):
    stopwords = list(STOP_WORDS)
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    word_frequencies = {}
    for word in doc:
        if word.text.lower() not in stopwords and word.text.lower() not in punctuation:
            if word.text not in word_frequencies.keys():
                word_frequencies[word.text] = 1
            else:
                word_frequencies[word.text] += 1
    max_frequency = max(word_frequencies.values())
    sentence_tokens = [sent for sent in doc.sents]
    sentence_scores = {}
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word.text.lower()]
                else:
                    sentence_scores[sent] = word_frequencies[word.text.lower()]
    select_length = int(len(sentence_tokens) * 0.3)
    summary = nlargest(select_length, sentence_scores, key=sentence_scores.get)
    result = " ".join([token.text for token in summary])
    result = result.replace("\n", " ")
    return result

# Streamlit UI
st.title("Research Paper Summarizer")
st.sidebar.header("Upload PDF")
uploaded_file = st.sidebar.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())

    abstract = extract_abstract_from_pdf(tmp_file.name)

    # Remove the temporary file
    os.remove(tmp_file.name)

    if abstract:
        st.subheader("Abstract Extracted from PDF:")
        st.write(abstract)

        st.subheader("Summarized Text:")
        summary = summarize_text(abstract)
        st.write(summary)
    else:
        st.error("No abstract found in the PDF. Please choose another PDF.")
