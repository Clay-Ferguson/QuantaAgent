"""Makes a query to OpenAI's API and writes the response to a file."""

import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class AppOpenAI:
    """Makes calls to OpenAI"""

    def __init__(self, api_key, model, system_prompt, data_folder):
        self.api_key = api_key
        self.model = model
        self.system_prompt = system_prompt
        self.data_folder = data_folder

    def query(self, query, output_file_name, ts):
        """Makes a query to OpenAI's API and writes the response to a file."""
        dry_run = False  # Eventually we'll have dry_run as a config option
        ret = ""

        if dry_run:
            # If dry_run is True, we simulate the AI response by reading from a file
            # if we canfind that file or else we return a default response.
            answer_file = f"{self.data_folder}/dry-run-answer.md"

            # TODO: explain this dry-run-answer.md file in the README (or docs)
            # if the answer file exists, read it
            if os.path.exists(answer_file):
                print(f"Simulating AI Response by reading answer from {answer_file}")
                with open(answer_file, "r", encoding="utf-8") as file:
                    ret = file.read()
            else:
                ret = "Dry Run: No API call made."
        else:
            llm = ChatOpenAI(
                model=self.model, temperature=0.000001, api_key=self.api_key
            )

            prompt = ChatPromptTemplate.from_messages(
                [("system", self.system_prompt), ("user", "{input}")]
            )
            output_parser = StrOutputParser()
            chain = prompt | llm | output_parser
            print("Waiting for OpenAI...")
            ret = chain.invoke({"input": query})

        output = f"""
{ret}
____________________________________________________________________________________
Note: The above content is the response from OpenAI's API using the following prompt:

OpenAI Model Used: {self.model}

System Prompt: {self.system_prompt}

Timestamp: {ts}

User Prompt: {query}
"""

        # print("Answer: "+output)
        self.write_to_file(output_file_name, output)
        return ret

    def write_to_file(self, output_file_name, content):
        """Writes the content to a file."""

        filename = f"{self.data_folder}/{output_file_name}--A.md"

        # Write content to the file
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)

        print(f"Wrote File: {filename}")
