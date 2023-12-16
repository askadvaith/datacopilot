import openai
import requests
import pymysql
import langchain
import os
import constants
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
import mysql.connector as ms
#from langchain.chat_models import ChatHuggingFace  # Use ChatHuggingFace instead of ChatOpenAI
#from langchain.llms.huggingface import HuggingFace  # Import HuggingFace llm
#from transformers import AutoModelForCausalLM, AutoTokenizer

# Setting OpenAI API key
os.environ["OPENAI_API_KEY"] = constants.APIKEY2
openai.api_key = constants.APIKEY2
db = SQLDatabase.from_uri("mysql+pymysql://root:mysql@localhost:3306/mydataset")

while True:
    print("Runmodes:\n1. Data retrieval\n2. Data inference\n3. Follow up")
    runmode=int(input("Enter runmode: "))
    langchain.debug = True
    
    if runmode==1:
        context="""\n<<<CONTEXT>>>
    Table 'test' contains personal details of engineering students. "ID" is the column to look at in case asked about "database ID" or "ID". SRN stands for Student Registration Number. The two capital \
    letters in the SRN besides "PES" denotes the branch of study (CS=Computer Science, AM=AI and ML, EC=Electronics and Communication Engineering, EE=Electronics and Electrical Engineering, \
    BT=Biotechnology, ME=Mechanical Engineering) PRN stands for Permanent Registration Number. This table contains information of only \
    students who joined in 2023. DOB stands for date of birth."""
        chain = create_sql_query_chain(llm=ChatOpenAI(temperature=0,model="gpt-3.5-turbo-1106"), db=db)
        #chain = create_sql_query_chain(llm=ChatHuggingFace(temperature=0, huggingface=huggingface_config), db=db)
        query = input("Enter your query: ")
        n = "I want " + input("Enter number of records to be retrieved: ") + " records"
        sql_query = chain.invoke({"question": query+n,"context":context})
        print(sql_query) #finish with python
        main
        mycon=ms.connect(user="root",passwd="mysql",host="localhost",database="studentrecords")
        cur=mycon.cursor()
        cur.execute(sql_query)
        output=cur.fetchall()
        cur.close()
        mycon.close()
        print(output)


    
    if runmode==2:
        agent_executor = create_sql_agent(
        llm=ChatOpenAI(temperature=0,model="gpt-3.5-turbo-1106"),
        toolkit=SQLDatabaseToolkit(db=db, llm=OpenAI(temperature=0)),
        verbose=False,
        agent_type=AgentType.OPENAI_FUNCTIONS
        )
        context="""\n<<<CONTEXT>>>
    Table 'test' contains personal details of engineering students. "ID" is the column to look at in case asked about "database ID" or "ID". SRN stands for Student Registration Number. The two capital \
    letters in the SRN besides "PES" denotes the branch of study (CS=Computer Science, AM=AI and ML, EC=Electronics and Communication Engineering, EE=Electronics and Electrical Engineering, \
    BT=Biotechnology, ME=Mechanical Engineering) PRN stands for Permanent Registration Number. This table contains information of only \
    students who joined in 2023. DOB stands for date of birth. Make sure to do any computation related to the question step by step only, and display the steps you have taken to arrive at \
    your answer."""

        query=input("Enter your query: ")
        op=agent_executor.run(query+context)
        print(op)

        with open("cache.txt","w") as cache:
            cache.write(op)

    if runmode==3:
        query=input("Enter your follow up query: ")
        with open("cache.txt") as cache:
            fcon=cache.read()
        messages = [{"role": "user", "content": query +"\nYou will be asked a question related to output you have previously generated, and asked to draw some \
inference from that. If you are not able to answer the given question with the information available under 'PREVIOUS OUTPUT', then return 'idk' as your only response.\
This was the previous output based on which you have to answer:\n<<<PREVIOUS OUTPUT>>>\n"+fcon}]
        reply = openai.ChatCompletion.create(model="gpt-3.5-turbo-1106",messages = messages,temperature=0)
        answer=reply.choices[0].message["content"]
        print(answer)
        







'''
loader=TextLoader("cache.txt")
index=VectorstoreIndexCreator().from_loaders([loader])
query=input("Enter your query: ")
op=index.query(query,llm=ChatOpenAI(temperature=0,model="gpt-3.5-turbo-1106"))
print(op)

agent_executor = create_sql_agent(
llm=ChatOpenAI(temperature=0,model="gpt-3.5-turbo-1106"),
toolkit=SQLDatabaseToolkit(db=db, llm=OpenAI(temperature=0)),
verbose=False,
agent_type=AgentType.OPENAI_FUNCTIONS
)
with open("cache.txt","r") as cache:
    prev=cache.read()
context=f"""\n<<<CONTEXT>>>
You will be asked a question related to output you have previously generated, and asked to draw some inference from that. This was the previous output based on which you have to answer: \
{prev}\nONLY if necessary to answer the question will you actually access the database. 
Table 'test' contains personal details of engineering students. "ID" is the column to look at in case asked about "database ID" or "ID". SRN stands for Student Registration Number. The two capital \
letters in the SRN besides "PES" denotes the branch of study (CS=Computer Science, AM=AI and ML, EC=Electronics and Communication Engineering, EE=Electronics and Electrical Engineering, \
BT=Biotechnology, ME=Mechanical Engineering) PRN stands for Permanent Registration Number. This table contains information of only \
students who joined in 2023. DOB stands for date of birth. Make sure to do any computation related to the question step by step only, and display the steps you have taken to arrive at \
your answer."""
query=input("Enter your query: ")
op=agent_executor.run(query+context)
print(op)    
'''
    
'''    
    agent_executor = create_sql_agent(
        llm=ChatOpenAI(temperature=0,model="gpt-3.5-turbo-1106"),
        toolkit=SQLDatabaseToolkit(db=db, llm=OpenAI(temperature=0)),
        verbose=False,
        agent_type=AgentType.OPENAI_FUNCTIONS
    )
    context="""\n<<<CONTEXT>>>
    Table 'test' contains personal details of engineering students. "ID" is the column to look at in case asked about "database ID" or "ID". SRN stands for Student Registration Number. The two capital \
    letters in the SRN besides "PES" denotes the branch of study (CS=Computer Science, AM=AI and ML, EC=Electronics and Communication Engineering, EE=Electronics and Electrical Engineering, \
    BT=Biotechnology, ME=Mechanical Engineering) PRN stands for Permanent Registration Number. This table contains information of only \
    students who joined in 2023. DOB stands for date of birth. When asked for "student details", display all details that are stored in the database about that/\
    those student(s). If asked any question relating to previously returned results, then look in the "PREVIOUS OUTPUT" for context. \
    For example:\nUser: Give me a list of students with ID less than 100.\nLLM: [numbered list of students]\nUser: Tell me the email of the first \
    student.\nLLM: [gives email of the first student from the list by looking in "PREVIOUS OUTPUT"] \n<<<PREVIOUS OUTPUT>>>\n"""

    query=input("Enter your query: ")

    op=agent_executor.run(query+context)
    print(op)

    mem=[]
    if len(mem)<=3:
        mem.append(op)
    else:
        del mem[0]
        mem.append(op)

    for i in mem:
        context+=(i+"\n")
    
    cont=input("Continue? (y/n): ")
    if cont.lower()=="n":
        break


    

'''

# two options: one being data inference and one being data retrieval?
# memory - nonexistent rn









