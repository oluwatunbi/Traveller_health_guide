import asyncio
import os
import logging


from openai import AsyncOpenAI
from semantic_kernel import Kernel
from semantic_kernel.agents import AgentGroupChat, ChatCompletionAgent
from semantic_kernel.agents.strategies import (
    KernelFunctionSelectionStrategy,
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



# create tools 
get_disease_function = KernelFunctionFromPrompt(
    function_name = "get_disease",
    prompt = """ Given a country(e.g Nigeria) and city(e.g Lagos), get the endemic and outbreak prone diseases
    a traveller should be aware of in the country or city"""
 )
    
  
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

async def main():
    print("Hello sermantic kernel")
    # create a single kernel instance for all agents.
    kernel = create_kernel()

    # setup logger with rich
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )
    logger = logging.getLogger("rich")
    logger.info("Starting health agent...")
    
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
        kernel= kernel,
        name = "vaccine_locator",
        instructions = """
        your responsibility is to provide information about vaccines available
        for the diseases detected by the {Disease_intelligent_agent} and where they can get the vaccine. """
    )

    Vaccine_booker_agent = ChatCompletionAgent(
        kernel = kernel,
        name = "vaccine_booker",
        instructions = """
        Your responsibility is to help user book day and time they can get their vaccines from
        vaccine clinics """
    )
  
    
    

    # Create a termination function how the user can exit the chat
    termination_key = "Done"
    termination_function = KernelFunctionFromPrompt(
        function_name = "termination",
        prompt = f"""
        Determine if the user response has been fullified or
        if the user has existed the chat.
        if the user has gotten a response from all the participates
        then user response is fullified and the chat should be terminated.{termination_key}
        if the user has exited the chat, then the chat should be terminated.
    
        print("🔁 [DEBUG] Last Message Sender:", last_message.sender)
        print("🧾 [DEBUG] Last Message Content:", last_message.content)

        Response:
        {{{{$lastmessage}}}}
        """,
    )

   
  
     
    

    # craete the agent group caht with selection and termination function
    chat = AgentGroupChat(
        agents = [Disease_intelligent_agent, Vaccine_locator_agent, Vaccine_booker_agent],
  

        termination_strategy = KernelFunctionTerminationStrategy(
            agents = [Vaccine_booker_agent],
            function = termination_function,
            kernel = kernel,
            result_parser= lambda result: termination_key in str(result.value[0]).lower(),
            history_variable_name = "lastmessage",
            maximum_iterations = 10,
        ), 
    )

    # create a chat lop bettween agent and user
    is_complete: bool = False
    while not is_complete:
        # collect user input
        user_input = input("User > ").strip()
        if not user_input:
            continue
        if user_input.lower() == "exit":
            is_complete = True
            break

        # add current user input to the chat
        await chat.add_chat_message(message = user_input)

        try:
            async for response in chat.invoke():
                if response is None or not response.name:
                    continue 
                print()
                print(f"# {response.name.upper()}:\n{response.content}")
        except Exception as e:
            print(f"Error: {e}")

        # Reset convesation
        chat.is_complete = False



if __name__ == "__main__":
    asyncio.run(main())