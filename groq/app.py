import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import time

load_dotenv()

##load the groq api
groq_api_key = os.getenv("GROQ_API_KEY")

if "vector" not in st.session_state:
    st.session_state.embeddings = OllamaEmbeddings()
    st.session_state.loader=WebBaseLoader("https://docs.smith.langchain.com/")
    st.session_state.docs=st.session_state.loader.load()
    st.session_state.text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
    st.session_state.final_documents=st.session_state.text_splitter.split_documents(st.session_state.docs)
    st.session_state.vector=FAISS.from_documents(st.session_state.final_documents,st.session_state.embeddings)
    
st.title("Groq Demo")
llm = ChatGroq(groq_api_key=groq_api_key,
               model_name="llama3-70b-8192")

prompt=ChatPromptTemplate.from_template("""
                                        Answer the questions based on the provided context only.
                                        Please provide the most accurate response based on the question.
                                        <context>
                                        {context}
                                        </context>
                                        Question:{input}
                                        """)

document_chain = create_stuff_documents_chain(llm,prompt)
retriver = st.session_state.vector.as_retriever()
retrival_chain = create_retrieval_chain(retriver,document_chain)
prompt = st.text_input("Input your propmt here")

if prompt:
    start = time.process_time()
    response = retrival_chain.invoke({"input":prompt})
    print("Response time :",time.process_time() - start)
    st.write(response["answer"])

    ##with a streamlit expander
    with st.expander("Document Similarity Search"):
        # find the relevant chunks
        for i, doc in enumerate(response["context"]):
            st.write(doc.page_content)
            st.write("--------------------------------------------------------")

