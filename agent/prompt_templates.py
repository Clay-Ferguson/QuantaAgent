"""Contains the prompt templates for the agent."""

import os
from agent.tags import (
    TAG_BLOCK_INJECT,
    TAG_INJECT_BEGIN,
    TAG_INJECT_END,
    TAG_FILE_BEGIN,
    TAG_FILE_END,
    TAG_NEW_FILE_BEGIN,
    TAG_NEW_FILE_END,
    DIVIDER,
)

# TODO: Lots of this verbiage says "code" when it can really be anything else (HTML, CSS) so maybe reword and use "content" instead of "code"


class PromptTemplates:
    """Contains the prompt templates for the agent."""

    @staticmethod
    def get_file_content_block(file_name, content):
        """Returns a file content block for the given file name and content."""
        return f"""
{TAG_FILE_BEGIN} {file_name}
{content}
{TAG_FILE_END} {file_name}
"""

    @staticmethod
    def get_file_insertion_instructions():
        """Returns instructions for providing the new code."""

        return f"""
If I have sent you individual file(s) and asked you to modify them, in the prompt text above,
then each file is delimited with `{TAG_FILE_BEGIN} ${{FileName}}` and `{TAG_FILE_END} ${{FileName}}` tags, so you can see what the full content of each file is along with it's filename.
Note that the actual file content for each file begins on the next line AFTER the `{TAG_FILE_BEGIN}` line, and ends on the line BEFORE the `{TAG_FILE_END}` line.

Please provide me with the new version(s) of the file(s) by using the following format, where you replace {{new_content}} with the new content of the file, and put the filename
in place of `FileName` without the `${{}}` tags. Do not alter the filenames at all, or remove any leading slashes. 

// {TAG_FILE_BEGIN} FileName
{{new_content}}
// {TAG_FILE_END} FileName

If you didn't find it necessary to edit a file, you can just omit it from your response. 
If I wasn't asking you to modify any code at all don't include any {TAG_FILE_BEGIN} or {TAG_FILE_END} blocks in your response.
"""

    @staticmethod
    def get_block_insertion_instructions():
        """Returns instructions for providing the new code."""

        return f"""

If I was asking you to add some new code, in the prompt above, then to provide me with the new code, use the following strategy: 
Notice that there are sections named `// {TAG_BLOCK_INJECT} {{Name}}` in the code I gave you. 
I'd like for you to show me just what I need to insert into each of those `{TAG_BLOCK_INJECT}` sections of the code. 
So when you show code, show only the changes and show the changes like this format in your response:

// {TAG_INJECT_BEGIN} {{Name}}
... the content to insert ...
// {TAG_INJECT_END} 

Note that the `//` in `// {TAG_BLOCK_INJECT} {{Name}}` is there becasue that example is for Java style comments; however, you may also find 
`-- {TAG_BLOCK_INJECT} {{Name}}` for SQL style comments, or `# {TAG_BLOCK_INJECT} {{Name}}` for Python style comments, and you will handle those also.
You may not need to inject into some of the `{TAG_BLOCK_INJECT}` locations. 
These `{TAG_BLOCK_INJECT}` points are just for you to refer to which places the code needs to be inserted, and to provide it back to me in a machine parsable way.

In the format example above, for the `{TAG_INJECT_BEGIN}` and `{TAG_INJECT_END}` lines, I've given `//` as the comment prefix in the example, 
but you should use whatever comment prefix is appropriate based on the language (or file format) you're working with. 
If there's no comment prefix for the language, just use `//` for the prefix.
"""

    @staticmethod
    def get_create_files_instructions():
        """Returns instructions for creating new files."""

        return f"""
If I asked you to create new files or projects, then you should provide the content of the new files in the following format, instead of your usual markdown format:

{TAG_NEW_FILE_BEGIN} /my/folder/file.txt
... content of file...
{TAG_NEW_FILE_END} /my/folder/file.txt

Make the content of the file the actual content, not a markdown representation of the content. 
You should of course use that format for as many files as you need to create. 
If you're modifying an existing project then the filenames should be relative to the root of the project, and should start with a slash.
For example a file in the project root folder would be named like `/my_root_file.txt`.
However, if you were asked to create a completely new project, you should insert a project folder name at the front all paths, but still start with a slash.
"""

    @staticmethod
    def build_folder_content(folder_path, ext_set, source_folder_len):
        """Builds the content of a folder. Which will contain all the filenames and their content."""
        print(f"Building content for folder: {folder_path}")

        content = f"""{DIVIDER}

Below is the content of the files in the folder named {folder_path} (using {TAG_FILE_BEGIN} and {TAG_FILE_END} tags to delimit the files):
        """
        for dirpath, _, filenames in os.walk(folder_path):
            for filename in filenames:
                # Check the file extension
                _, ext = os.path.splitext(filename)
                if ext.lower() in ext_set:
                    # build the full path
                    path = os.path.join(dirpath, filename)
                    # get the file name relative to the source folder
                    file_name = path[source_folder_len:]
                    with open(path, "r", encoding="utf-8") as file:
                        file_content = file.read()
                        content += PromptTemplates.get_file_content_block(
                            file_name, file_content
                        )

        return content
