import openai
import requests
import pymysql
import langchain
import os
import streamlit as st
#import constants
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain.chains.sql_database.query import create_sql_query_chain
from langchain.chat_models import ChatOpenAI
from langchain.llms.openai import OpenAI
from langchain.sql_database import SQLDatabase
from langchain.utilities import SQLDatabase
from langchain.document_loaders import TextLoader, DirectoryLoader
from langchain.indexes import VectorstoreIndexCreator
from warnings import catch_warnings


# Setting OpenAI API key


db = SQLDatabase.from_uri("mysql+pymysql://root:mysql@localhost:3306/mydataset")
langchain.debug=True

context = """\n<<<CONTEXT>>>
Table 'test' contains personal details of engineering students. "ID" is the column to look at in case asked about "database ID" or "ID". SRN stands for Student Registration Number. The two capital \
letters in the SRN besides "PES" denotes the branch of study (CS=Computer Science, AM=AI and ML, EC=Electronics and Communication Engineering, EE=Electronics and Electrical Engineering, \
BT=Biotechnology, ME=Mechanical Engineering.) All these abbreviations like CS, AM, EC, EE, BT and ME denote the branch of study or the degree the student is pursuing. If asked about these \
abbreviations, the user is referring to what the students are studying for which you have to check if the SRN contains the required abbreviation(CS=Computer Science, AM=AI and ML, \
EC=Electronics and Communication Engineering, EE=Electronics and Electrical Engineering, BT=Biotechnology, ME=Mechanical Engineering). Don't check if the SRN contains any other \
abbreviation. \nExample:\nUser: Give me a list of students in CS. \
\nContext: You're supposed to give a list of people studying CS,  that is Computer Science.\
\nAI: "SELECT * \nFROM test \nWHERE `SRN` LIKE '%CS%'" \nPRN stands for Permanent Registration Number. This table contains information of only \
students who joined in 2023. DOB stands for date of birth. Make sure to do any computation related to the question step by step only, and display all the steps you have taken to arrive at \
your answer."""



def data_retrieval(user_input, record_count):
    
    with catch_warnings():  # imports and handles warnings within the function
        chain = create_sql_query_chain(llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo-1106"), db=db)
    
    n = f"I want {record_count} records"
    
    sql_query = chain.invoke({"question": user_input + n, "context": context})
    mycon=pymysql.connect(user="root",passwd="mysql",host="localhost",database="mydataset")
    cur=mycon.cursor()
    cur.execute(sql_query)
    output=cur.fetchall()
    cur.close()
    mycon.close()
    with open("cache.txt", "w") as cache:
        cache.write(str(output))
    return output


def data_inference(user_input, db=db):
    agent_executor = create_sql_agent(
        llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo-1106"),
        toolkit=SQLDatabaseToolkit(db=db, llm=OpenAI(temperature=0)),
        verbose=False,
        agent_type=AgentType.OPENAI_FUNCTIONS
    )

    # Assuming the query here originates from user input in Streamlit
    query = user_input

    op = agent_executor.run(query + context)
    print(op)

    with open("cache.txt", "w") as cache:
        cache.write(str(op))
        
    return op


def follow_up(user_input, db=db):
    with open("cache.txt") as cache:
        fcon = cache.read()
        messages = [{
            "role": "user",
            "content": user_input + "\nYou will be asked a question related to output you have previously generated, and asked to draw some inference from that. If you are not able to answer \
the given question with the information available under 'PREVIOUS OUTPUT', then return 'idk' as your only response. This is true for any case where you're unable to answer the question; \
always return 'idk' as your only response if you're unable to answer the question. SRN stands for Student Registration Number, and is of the \
format 'PES1UG23XXyyy'. The two capital letters in the SRN (indicated by 'XX' here) besides 'PES' denotes the branch of study (CS=Computer Science, AM=AI and ML, EC=Electronics and Communication Engineering, EE=Electronics and Electrical Engineering, \
BT=Biotechnology/Biotech, ME=Mechanical Engineering). All these abbreviations like CS, AM, EC, EE, BT and ME denote the branch of study or the degree the student is pursuing. If asked about these \
abbreviations, the user is referring to what the students are studying for which you have to check if the SRN contains the required abbreviation(CS=Computer Science, AM=AI and ML, \
EC=Electronics and Communication Engineering, EE=Electronics and Electrical Engineering, BT=Biotechnology, ME=Mechanical Engineering). Don't check if the SRN contains any other \
abbreviation. 'yyy' here refers to some sequence of 5 numbers. PRN stands for Permanent Registration Number, and is of the format 'PES12023zzzzz' where 'zzzzz' denotes some sequence of 5 \
numbers. This is the previous output based on which you have to \
answer:\n<<<PREVIOUS OUTPUT>>>\n" + fcon
        }]
        
        reply = openai.ChatCompletion.create(model="gpt-3.5-turbo-1106", messages=messages, temperature=0)
        answer = reply.choices[0].message["content"]
        if answer.strip()!="idk":
            return answer
        
        agent_executor = create_sql_agent(
        llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo-1106"),
        toolkit=SQLDatabaseToolkit(db=db, llm=OpenAI(temperature=0)),
        verbose=False,
        agent_type=AgentType.OPENAI_FUNCTIONS
        )
        fcontext = "\n<<<CONTEXT>>>\n\
    You will be asked a question related to output you have previously generated, and asked to draw some inference from that. The previous output based on which you have to answer \
    is: \n<<<PREVIOUS OUTPUT>>>\n" + fcon +"\nYou will also need additional information from the database. \n<<<DATABASE INFORMATION>>>\n"+context[14::]
        op = agent_executor.run(user_input + fcontext)
        return op







# Streamlit app layout with improved styling
def main():
    # Set page configuration
    st.set_page_config(
        page_title="Easy Data Retrieval and Inferencing Using Python and LangChain",
        page_icon=":speech_balloon:",
        layout="wide",
    )

    # Set a more vivid purple theme
    vivid_purple = "#7E3AC1"
    st.markdown(
        f"""
        <style>
            body {{
                background-color: {vivid_purple};
                color: #ffffff;
            }}
            .css-1aumxhk {{
                width: 85%;
                max-width: 85%;
            }}
            .sidebar .sidebar-content {{
                background-color: {vivid_purple};
            }}
            .css-1s0lmgv {{
                color: #c9c4d1;
            }}
            .css-17eq0hr {{
                color: #ffffff;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Main content for chat-like UI
    st.title("Easy Data Retrieval and Inferencing Using Python and LangChain")

    # Display user input and LLM-generated response in a chat-like format
    with st.form(key='chat_form'):
        col1, col2 = st.columns([4, 1])
        with col1:
            user_input = st.text_area("Enter a query:", height=100)
            resno = st.text_input("Enter the number of records to retrieve if applicable:")
        with col2:
            options = ["Data Retrieval", "Data Inference", "Follow Up"]
            selected_option = st.selectbox("Select an Option", options)
            st.write("")  # Adjusts spacing
            submit_button = st.form_submit_button(label='Send')
        

          # If the input field is not empty
        if selected_option == "Data Retrieval":
            if submit_button:
                if user_input and resno:
                        response = data_retrieval(user_input,resno)
                        st.text("")
                        st.text("You: " + user_input)
                        st.text("AI: " + str(response))
        elif selected_option == "Data Inference":
            if submit_button:
                if user_input:
                    response = data_inference(user_input)
                    st.text("")
                    st.text("You: " + user_input)
                    st.text("AI: " + response)
        elif selected_option == "Follow Up":
                if submit_button:
                    if user_input:
                        response = follow_up(user_input)
                        st.text("")
                        st.text("You: " + user_input)
                        st.text("AI: "+ response)

            

if __name__ == "__main__":
    main()
