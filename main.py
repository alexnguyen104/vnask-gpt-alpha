from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
import asyncio

import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI-API-KEY')
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP-API-KEY')

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["OPENWEATHERMAP_API_KEY"] = OPENWEATHERMAP_API_KEY

# default language
language = "English"

model = ChatOpenAI(model="gpt-4")

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You must only answer questions related to Vietnam, otherwise politely reject it. Your name is VNAsk-GPT or Tèo. Answer in {language}",
        ),
        MessagesPlaceholder(variable_name="history"),
        MessagesPlaceholder(variable_name="input"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ]
)

wrapper = DuckDuckGoSearchAPIWrapper(region="uk-en")
search_tool = DuckDuckGoSearchResults(api_wrapper=wrapper, source="news")
# weather_tool = load_tools(["openweathermap-api"], model)

tools = [search_tool]
# tools.extend(weather_tool)

agent = create_tool_calling_agent(llm=model, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False, handle_parsing_errors=True)

# chain = prompt | model

chat_history = []

async def streaming():
    ai_output = ''
    async for event in agent_executor.astream_events({"input": [HumanMessage(content=mes)], "history": chat_history[-N_LAST_MESSAGE * 2:], "language": language}, version='v2'):
            if event["event"] == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                ai_output += chunk.content
                print(chunk.content, end="", flush=True)

    # add to history
    chat_history.append(AIMessage(content=ai_output))
    
while True:
    mes = input("\nMessage: ")
    if mes.lower() == "vie":
        language = "Vietnamese"
        print("Change language to Vietnamese")
        continue
    elif mes.lower() == "eng":
        language = "English"
        print("Change language to English")
        continue
    elif mes.lower() == "exit":
        break
    elif mes.lower() == "his":
        for i in chat_history:
            print("- " + str(i))
        continue

    # add to history
    N_LAST_MESSAGE = 3
    ai_output = ""
    chat_history.append(HumanMessage(content=mes))

    # streaming answer  
    asyncio.run(streaming())