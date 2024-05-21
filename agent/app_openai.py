"""Makes a query to OpenAI's API and writes the response to a file."""

import os
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, BaseMessage, SystemMessage
from langgraph.prebuilt import chat_agent_executor

from agent.app_config import AppConfig
from agent.models import TextBlock
from agent.prompt_utils import PromptUtils
from agent.utils import Utils
from agent.tools.block_mods import (
    UpdateBlockTool,
    CreateFileTool,
    UpdateFileTool,
    update_block,
    create_file,
    update_file,
)


class AppOpenAI:
    """Makes calls to OpenAI"""

    dry_run: bool = False

    def __init__(
        self,
        mode: str,
        source_folder: str,
        api_key: str,
        model: str,
        system_prompt: str,
        data_folder: str,
        blocks: Dict[str, TextBlock] = {},
        st=None,
    ):
        self.mode = mode
        self.source_folder: str = source_folder
        self.api_key: str = api_key
        self.model: str = model
        self.system_prompt: str = system_prompt
        self.data_folder: str = data_folder
        self.blocks = blocks
        self.st = st

    def query(
        self,
        messages: List[BaseMessage],
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

            if os.path.isfile(answer_file):
                print(f"Simulating AI Response by reading answer from {answer_file}")
                ret = Utils.read_file(answer_file)
            else:
                ret = "Dry Run: No API call made."
        else:
            # NOTE: Pylance is incorrectly choking on the following line, so leave the `type: ignore` in place
            llm = ChatOpenAI(model=self.model, temperature=0.0, api_key=self.api_key, verbose=True)  # type: ignore

            # Check the first 'message' to see if it's a SystemMessage and if not then insert one
            if len(messages) == 0 or not isinstance(messages[0], SystemMessage):
                messages.insert(0, SystemMessage(content=self.system_prompt))
            # else we set the first message to the system prompt
            else:
                messages[0] = SystemMessage(content=self.system_prompt)

            human_message = HumanMessage(content=query)

            if self.st is not None:
                self.st.session_state.p_user_inputs[id(human_message)] = input_prompt

            messages.append(human_message)

            if AppConfig.tool_use:
                # https://python.langchain.com/v0.2/docs/tutorials/agents/
                if AppConfig.agentic:
                    tools = [
                        UpdateBlockTool("Block Updater Tool", self.blocks),
                        CreateFileTool("File Creator Tool", self.source_folder),
                        UpdateFileTool("File Updater Tool", self.source_folder),
                    ]  # type: ignore
                    agent_executor = chat_agent_executor.create_tool_calling_executor(
                        llm, tools
                    )
                    initial_message_len = len(messages)
                    response = agent_executor.invoke({"messages": list(messages)})
                    # print(f"Response: {response}")
                    resp_messages = response["messages"]

                    new_messages = resp_messages[initial_message_len:]
                    ret = ""
                    ai_response: int = 0
                    for message in new_messages:
                        if isinstance(message, AIMessage):
                            ai_response += 1
                            content = message.content
                            if not content:
                                content = "No Content. Probably a tool call."
                            ret += f"AI Response {ai_response}:\n{content}\n==============\n"  # type: ignore

                    # Agents may add multiple new messages, so we need to update the messages list
                    messages[:] = resp_messages

                else:
                    # With this approach (as opposed to the agent_executor above), and it will be designating a call to
                    # the @tool annotated functions, but the tool won't have been executed automatically
                    # in this non-agentic approach. So, we need to call the tool manually, in this case, however we will
                    # probably always keep `AppConfig.agentic=True` permanent in this app, so this block of code is just for
                    # reference, and we will probably never use it.
                    tools = [update_block, create_file, update_file]
                    llm_with_tools = llm.bind_tools(tools)
                    response = llm_with_tools.invoke(list(messages))
                    print(f"Response: {response}")
                    ret = response.content  # type: ignore
                    messages.append(AIMessage(content=response.content))

            else:
                response = llm.invoke(list(messages))
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
