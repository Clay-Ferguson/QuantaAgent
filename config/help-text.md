# Coding Assistant

The Coding Assistant is a chatbot which will help you write or refactor code. You simply provide the root level folder in the `config.yaml`, and then you can reference specific files, folders, or code blocks in your prompt as explained below:

**Referencing Code in your Prompt**

To bring your code into the context of a given chat thread, you need to mention it using `file(), folder(), or block()` as follows:

* To reference your *entire* project's code you can mention `folder(/)` in your prompt to refer to it which will bring all your project files into the AI's context, and allow any arbitrary changes, but beware this uses up more of your AI credits that only referencing the specific files or folders you need to.

* To reference a folder, you can mention `folder(/folder_name/)` to bring all the files in that folder into the AI's context. Note that this must end with a slash. 

* To reference a specific file, you can use `file(/file_name)` to bring that file into the AI's context.

* To reference a specific `Named Block` you can use `block(MyBlockName)` to bring that block of code into the AI's context. 

To define `MyBlockName` in your code, in order to refer to it in prompts, you simply wrap some of your code with something like the following, using Python comment syntax for example:

```py
# block_begin MyBlock
...some python code...
# block_end
```

Note that the block_begin/block_end lines are comments. The comments characters currently supported are `//`, `--`, and `#`