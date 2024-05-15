# Named Blocks

You can define `Named Blocks` in your code to identify specific areas which you'd like to ask questions about by name (name of a block), to save you from having to continually paste those sections of code into AI prompts.

In other words, this tool will [optionally] scan your project and extract named snippets (or sections of code) called `blocks` (i.e. fragments of files, that you identify using structured comments, described below) which are then automatically injected into your prompts by using an assigned name you give to each fragment. 

In summary, this lets you name sections of your code, in any files inside your project, and then refer to those sections by name in prompts, in such a way that the prompt injects the actual code block wherever you mention it's name. In this way you can write prompts involving sections of your code without the need to cut-and-paste from your code into the prompt by hand, and without referencing the entire file in your prompt.

### How it Works (Identifying Blocks)

Named blocks are defined using this syntax to wrap part of your files:

```sql
-- block_begin SQL_Scripts
...all the scripts
-- block_end 
```

--or--

```java
// block_begin My_Java
...all the code
// block_end 
```

In the syntax above, the text that comes after the `block_begin` is considered the `Block Name` and, as shown in the example above, the `Block Names` are usable in prompts. So, from the example above, `${SQL_Scripts}` and `${My_Java}` when used in a prompt, will be replaced with the block content (actual source).

Note: If only `block_begin` exists and `block_end` doesn't exist, the block will end at the end of the file.

Note: The relative filename is also a valid "block name" and will insert the entire content of the specified file into the prompt. So you can simply put `${/path/to/my/file.md}` in a prompt, and it will inject the entire content of the file into the prompt. Note that the configured `source_folder` is the assumed prefix (base folder) for all of these kinds of file names. 

You can also inject an entire folder structure into your prompt by using `${/my/folder/name/}` syntax. This injects each filename and file content, in the entire folder, into the prompt.

So, in summary, The tool will scan all your source files (inside `source_folder`) and collect all these "Named Blocks" of code, and then you can just use the names themselves in your prompt templates, to inject the block content. You can also use the name of the file to inject the entire file, or the name of a folder to inject the entire folder. 

