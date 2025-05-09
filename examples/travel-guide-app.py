import asyncio
import os
import logging
import chainlit as cl

from openai import AsyncOpenAI
from semantic_kernel import Kernel
from semantic_kernel.agents import AgentGroupChat, ChatCompletionAgent
from semantic_kernel.agents.strategies import (
    KernelFunctionTerminationStrategy,
)

from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.contents import ChatHistory, ChatHistoryTruncationReducer
from semantic_kernel.functions import KernelFunctionFromPrompt
from semantic_kernel.utils.logging import setup_logging
from rich.logging import RichHandler


"""
This is a prototype of a health agent that can help traveller/tourist to find
endemic and outbreaked prone diseases where you are travelling to and also help
find vaccines to help prevent contracting these diseases."""


# global variable
kernel = None,
chat = None,


# setup logger with rich
    
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
    )
logger = logging.getLogger("rich")
logger.info("Starting health agent...")   
  
# create a kernel instance
def create_kernel() -> Kernel:
    """Creates a Kernel instance with an Azure OpenAI ChatCompletion service."""
    kernel = Kernel()

    chat_client = AsyncOpenAI(
        api_key=os.environ["GITHUB_TOKEN"], 
        base_url="https://models.inference.ai.azure.com")
    chat_completion_service = OpenAIChatCompletion(ai_model_id = "gpt-4o", async_client = chat_client)
    kernel.add_service(chat_completion_service)
    return kernel

# create a single kernel instance for all agents.
kernel = create_kernel()
# create chat completion agents using the same kernel.
Disease_intelligent_agent = ChatCompletionAgent(
    kernel=kernel,
    name = "disease_intelligent",
    instructions = """
    your resonsibility is to provide information about endemic and outbreak prone dieases
    in the country and city the user is travelling to using the right tools and ensuring
    the information is accurate and up to date. """,

    )

Vaccine_locator_agent = ChatCompletionAgent(
    kernel=kernel,
    name="vaccine_locator",
    instructions="""
    Provide information about vaccines available for detected diseases and where to get them.
    """,
)


Vaccine_booker_agent = ChatCompletionAgent(
    kernel = kernel,
    name = "vaccine_booker",
    instructions = """
    Your responsibility is to help user book day and time they can get their vaccines from
    vaccine clinics """
    )

termination_key = "Done"
termination_function = KernelFunctionFromPrompt(
    function_name = "termination",
    prompt = f"""
    Determine if the user has gotten a reponse from all agents in one turn 
    then terminate the chat the chat should be terminated.{termination_key}
    if the user has exited the chat, then the chat should be terminated.
    No agent should take more than one turn to respond to the User.
    
    RULE:
    1. No agent should take more than one turn to respond to the User.


    Response:
    {{{{$lastmessage}}}}
    """,
    )
  
chat = AgentGroupChat(
    agents = [Disease_intelligent_agent, Vaccine_booker_agent],
    termination_strategy = KernelFunctionTerminationStrategy(
        function = termination_function,
        kernel = kernel,
        result_parser= lambda result: termination_key in str(result.value[0]).lower(),
        history_variable_name = "lastmessage",
        maximum_iterations = 10,
        ), 
    )


# intiaite the agent
@cl.on_chat_start
async def on_chat_start():
    global kernel

  
    await cl.Message(
        content = "welcome to the health agent, Which country/ city will you like to visit?").send()


# Chainlit event listener for messages
@cl.on_message
async def handle_message(message: cl.Message):
    """Handles incoming user messages using Chainlit."""
    user_input = message.content.strip()
    if not user_input:
        return

    await chat.add_chat_message(message=user_input)

    try:
        async for response in chat.invoke():
            if response and response.name:
                await cl.Message(content=f"# {response.name.upper()}:\n{response.content}").send()
    except Exception as e:
        await cl.Message(content=f"Error: {e}").send()