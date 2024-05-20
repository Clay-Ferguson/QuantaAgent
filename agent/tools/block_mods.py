"""Tools for updating blocks of text."""

from typing import Dict, Optional, Type

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool
from agent.models import TextBlock


class UpdateBlockInput(BaseModel):
    block_name: str = Field(description="Block Name")
    block_content: str = Field(description="Block Content")


# This tool annotation is not needed when the UpdateBlockTool class below, is used
# and mixing the two is also not allowed by Langchain and would cause problems.
#
# @tool("update_block", args_schema=UpdateBlockInput, return_direct=False)
def update_block(block_name: str, block_content: str) -> str:
    """Updates and saves a named block of text"""
    return f"Tool Call: update_block({block_name}, {block_content})"


class UpdateBlockTool(BaseTool):
    """Tool to update a block of text."""

    # Warning there is a reference to this block name in "block_update_instructions.txt", although things do work
    # fine even without mentioning "block_update" in those instructions.
    name = "update_block"
    description = "useful for when you need to update blocks of text, with new content"
    args_schema: Type[BaseModel] = UpdateBlockInput
    return_direct: bool = False
    blocks: Dict[str, TextBlock] = {}

    def __init__(self, description, blocks):
        super().__init__(description=description)
        self.blocks = blocks

    def _run(
        self,
        block_name: str,
        block_content: str,
        # run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        msg = f"Tool Updated Block: {block_name} with content: {block_content}"
        block: Optional[TextBlock] = self.blocks.get(block_name)
        if block is not None:
            block.content = block_content
        return msg

    # This async stuff is optional and performance related, so for now we omit.
    # async def _arun(
    #     self,
    #     block_name: str, block_content: str,
    #     run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    # ) -> str:
    #     """Use the tool asynchronously."""
    #     # If the calculation is cheap, you can just delegate to the sync implementation
    #     # as shown below.
    #     # If the sync calculation is expensive, you should delete the entire _arun method.
    #     # LangChain will automatically provide a better implementation that will
    #     # kick off the task in a thread to make sure it doesn't block other async code.
    #     return self._run(block_name, block_content, run_manager=run_manager.get_sync())
