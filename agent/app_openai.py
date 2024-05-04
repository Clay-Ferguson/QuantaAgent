"""Makes a query to OpenAI's API and writes the response to a file."""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def ai_query(ts, api_key, model, system_prompt, data_folder, query):
    """Makes a query to OpenAI's API and writes the response to a file."""
    llm = ChatOpenAI(model=model, temperature=0.7, api_key=api_key)

    prompt = ChatPromptTemplate.from_messages(
        [("system", system_prompt), ("user", "{input}")]
    )
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    print("Waiting for OpenAI...")
    output = chain.invoke({"input": query})
    output += f"""
\n\n__________________________________________________________________________
# Query that was sent to OpenAI...

OpenAI Model Used: {model}

System Prompt: {system_prompt}

User Query: {query}
"""

    # print("Answer: "+output)
    write_to_file(data_folder, ts, output)


def write_to_file(data_folder, ts, content):
    """Writes the content to a file."""
    filename = f"{data_folder}/{ts}-answer.md"

    # Write content to the file
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)

    print(f"Wrote File: {filename}")
