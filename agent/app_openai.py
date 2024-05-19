"""Makes a query to OpenAI's API and writes the response to a file."""

import os
from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema import HumanMessage, AIMessage, BaseMessage, SystemMessage

from agent.prompt_utils import PromptUtils
from agent.utils import Utils


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
