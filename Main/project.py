import openai
import requests
import pymysql
import langchain
import os
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain.chains.sql_database.query import create_sql_query_chain
from langchain.chat_models import ChatOpenAI
from langchain.llms.openai import OpenAI
from langchain.sql_database import SQLDatabase
from langchain.utilities import SQLDatabase
#from langchain.chat_models import ChatHuggingFace  # Use ChatHuggingFace instead of ChatOpenAI
#from langchain.llms.huggingface import HuggingFace  # Import HuggingFace llm
#from transformers import AutoModelForCausalLM, AutoTokenizer

# Setting OpenAI API key


#huggingface test
''' 
model_path = "SUSTech/SUS-Chat-34B"
# model_path = "SUSTC/SUS-Chat-34B" # ModelScope
tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=False)
model = AutoModelForCausalLM.from_pretrained(
    model_path, device_map="auto", torch_dtype="auto"
).eval()
huggingface_config = {
    "model": model,
    "tokenizer": tokenizer,
}
'''

langchain.debug = True
db = SQLDatabase.from_uri("mysql+pymysql://root:mysql@localhost:3306/mydataset")
'''
chain = create_sql_query_chain(llm=ChatOpenAI(temperature=0,model="gpt-3.5-turbo-1106"), db=db)
#chain = create_sql_query_chain(llm=ChatHuggingFace(temperature=0, huggingface=huggingface_config), db=db)
sql_query = chain.invoke({"question": "What is my data about?"})
print(sql_query)
'''
agent_executor = create_sql_agent(
    llm=ChatOpenAI(temperature=0,model="gpt-3.5-turbo-1106"),
    toolkit=SQLDatabaseToolkit(db=db, llm=OpenAI(temperature=0)),
    verbose=False,
    agent_type=AgentType.OPENAI_FUNCTIONS
)
context="""\n<<<CONTEXT>>>
Table 'test' contains personal details of engineering students. "ID" is the column to look at in case asked about "database ID". SRN stands for Student Registration Number. The two capital \
letters in the SRN besides "PES" denotes the branch of study (CS=Computer Science, AM=AI and ML, EC=Electronics and Communication Engineering, EE=Electronics and Electrical Engineering, \
BT=Biotechnology, ME=Mechanical Engineering) PRN stands for Permanent Registration Number. This table contains information of only \
students who joined in 2023. DOB stands for date of birth. When querying the database, display all records returned from the query in the output."""

query=input("Enter your query: ")

print(agent_executor.run(query+context))



# two options: one being data inference and one being data retrieval?
# memory - nonexistent rn









