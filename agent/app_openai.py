"""Makes a query to OpenAI's API and writes the response to a file."""

import os
from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, BaseMessage, SystemMessage

from agent.prompt_utils import PromptUtils
from agent.utils import Utils

# DO NOT DELETE THESE IMPORTS
# from langchain_core.tools import tool
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.output_parsers.openai_tools import PydanticToolsParser
# from langchain_core.pydantic_v1 import BaseModel, Field


# DO NOT DELETE THIS FUNCTION
# This was part of some experimentation with Langchain Tool Use you'll find
# below which is commented out. Tool use doesn't fit into conversational flow
# as well as our approach does, so we're not using Langchain tools for now.
# @tool
# def update_block(block_name: str, block_content: str) -> str:
#     """Updates and saves a named block of text"""
#     return f"Tool Call: update_block({block_name}, {block_content})"

# DO NOT DELETE THIS CLASS
# Note that the docstrings here are crucial, as they will be passed along
# to the model along with the class name.
# This class not used for now, but the pydantic example below uses this
# class UpdateBlock(BaseModel):
#     """Updates and saves a named block of text"""
#     block_name: str = Field(..., description="Block Name")
#     block_content: str = Field(..., description="Block Content")


class AppOpenAI:
    """Makes calls to OpenAI"""

    dry_run: bool = False

    def __init__(
        self,
        mode: str,
        api_key: str,
        model: str,
        system_prompt: str,
        data_folder: str,
    ):
        self.mode = mode
        self.api_key: str = api_key
        self.model: str = model
        self.system_prompt: str = system_prompt
        self.data_folder: str = data_folder

    def query(
        self,
        messages: Optional[List[BaseMessage]],
        query: str,
        input_prompt: str,
        output_file_name: str,
        ts: str,
    ) -> str:
        """Makes a query to OpenAI's API and writes the response to a file."""
        ret: str = ""

        if self.dry_run:
            # If dry_run is True, we simulate the AI response by reading from a file
            # if we canfind that file or else we return a default response.
            answer_file: str = f"{self.data_folder}/dry-run-answer.txt"

            if os.path.exists(answer_file):
                print(f"Simulating AI Response by reading answer from {answer_file}")
                ret = Utils.read_file(answer_file)
            else:
                ret = "Dry Run: No API call made."
        else:
            # NOTE: Pylance is incorrectly choking on the following line, so leave the `type: ignore` in place
            llm = ChatOpenAI(model=self.model, temperature=0.0, api_key=self.api_key)  # type: ignore

            # Part of Langchain Tool Use experimentation
            # We're not useing pydantic for now, so we pass an actual method
            # llm_with_tools = llm.bind_tools([update_block])

            # messages is none this is a one-shot query with no prior context
            if messages is None:
                # We end up here for the command line interface, where we have no prior context
                messages = []

            # Check the first 'message' to see if it's a SystemMessage and if not then insert one
            if len(messages) == 0 or not isinstance(messages[0], SystemMessage):
                messages.insert(0, SystemMessage(content=self.system_prompt))
            # else we set the first message to the system prompt
            else:
                messages[0] = SystemMessage(content=self.system_prompt)

            human_message = HumanMessage(content=query)
            PromptUtils.user_inputs[id(human_message)] = input_prompt
            messages.append(human_message)

            # BEGIN_NON_PYDANTIC
            # response = llm_with_tools.invoke(list(messages))
            # ret = response.content  # type: ignore
            # BEGIN_PYDANTIC
            # chain = llm_with_tools | PydanticToolsParser(tools=[Updateblock])
            # response = chain.invoke(list(messages))
            # END_PYDANTIC

            response = llm(list(messages))
            ret = response.content  # type: ignore
            messages.append(AIMessage(content=response.content))

        output = f"""OpenAI Model Used: {self.model}, Mode: {self.mode}, Timestamp: {ts}
____________________________________________________________________________________
Input Prompt: 
{input_prompt}
____________________________________________________________________________________
LLM Output: 
{ret}
____________________________________________________________________________________
System Prompt: 
{self.system_prompt}
____________________________________________________________________________________
Final Prompt: 
{query}
"""

        filename = f"{self.data_folder}/{output_file_name}.txt"
        Utils.write_file(filename, output)
        print(f"Wrote Log File: {filename}")
        return ret
