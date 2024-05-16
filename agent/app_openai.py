"""Makes a query to OpenAI's API and writes the response to a file."""

import os
from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema import HumanMessage, AIMessage, BaseMessage

from agent.prompt_utils import PromptUtils
from agent.utils import Utils


class AppOpenAI:
    """Makes calls to OpenAI"""

    dry_run: bool = False

    def __init__(
        self,
        api_key: str,
        model: str,
        system_prompt: str,
        data_folder: str,
    ):
        self.api_key: str = api_key
        self.model: str = model
        self.system_prompt: str = system_prompt
        self.data_folder: str = data_folder

    def query(
        self,
        messages: Optional[List[BaseMessage]],
        query: str,
        user_input: str,
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
                with open(answer_file, "r", encoding="utf-8") as file:
                    ret = file.read()
            else:
                ret = "Dry Run: No API call made."
        else:
            # NOTE: Pylance is incorrectly choking on the following line, so leave the `type: ignore` in place
            llm = ChatOpenAI(model=self.model, temperature=0.0, api_key=self.api_key)  # type: ignore

            # messages is none this is a one-shot query with no prior context
            if messages is None:
                prompt = ChatPromptTemplate.from_messages(
                    [("system", self.system_prompt), ("user", "{input}")]
                )
                output_parser = StrOutputParser()
                chain = prompt | llm | output_parser
                print("Waiting for OpenAI...")
                ret = chain.invoke({"input": query})
            else:
                # Else we're doing a chat with context, so we append the question and also the answer, and leave
                # the self.chat_response as the last response.
                human_message = HumanMessage(content=query)
                PromptUtils.user_inputs[id(human_message)] = user_input
                messages.append(human_message)
                response = llm(list(messages))
                ret = response.content  # type: ignore
                messages.append(AIMessage(content=response.content))

        output = f"""
{ret}
____________________________________________________________________________________
Note: The above content is the response from OpenAI's API using the following prompt:

OpenAI Model Used: {self.model}

System Prompt: {self.system_prompt}

Timestamp: {ts}

User Prompt: {query}
"""

        self.write_to_file(output_file_name, output)
        return ret

    def write_to_file(self, output_file_name: str, content: str):
        """Writes the content to a file."""

        filename = f"{self.data_folder}/{output_file_name}--A.txt"
        Utils.write_file(filename, content)
        print(f"Wrote File: {filename}")
