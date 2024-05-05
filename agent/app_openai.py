"""Makes a query to OpenAI's API and writes the response to a file."""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class AppOpenAI:
    """Makes calls to OpenAI"""

    # TODO: Pass all these args, except for 'query' into a constructor
    def query(
        self, api_key, model, system_prompt, data_folder, query, output_file_name, ts
    ):
        """Makes a query to OpenAI's API and writes the response to a file."""
        dry_run = False  # Eventually we'll have dry_run as a config option
        ret = ""

        if dry_run:
            output = "Dry Run: No API call made."
        else:
            llm = ChatOpenAI(model=model, temperature=0.7, api_key=api_key)

            prompt = ChatPromptTemplate.from_messages(
                [("system", system_prompt), ("user", "{input}")]
            )
            output_parser = StrOutputParser()
            chain = prompt | llm | output_parser
            print("Waiting for OpenAI...")
            ret = chain.invoke({"input": query})
            output = ret

        output += f"""
\n\n____________________________________________________________________________________
Note: The above content is the response from OpenAI's API using the following prompt:

OpenAI Model Used: {model}

System Prompt: {system_prompt}

Timestamp: {ts}

User Prompt: {query}
"""

        # print("Answer: "+output)
        self.write_to_file(data_folder, output_file_name, output)
        return ret

    def write_to_file(self, data_folder, output_file_name, content):
        """Writes the content to a file."""

        filename = f"{data_folder}/{output_file_name}--A.md"

        # Write content to the file
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)

        print(f"Wrote File: {filename}")
