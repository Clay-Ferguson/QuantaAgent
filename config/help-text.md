# Coding Assistant

The Coding Assistant is a chatbot which will help you write or refactor code. You simply provide the root level folder in the `config.yaml`, and then you can reference specific files, folders, or code blocks in your prompt as explained below:

**Referencing Code in your Prompt**

* To reference your project files you need to mention `${/}`, which will bring all your project files into the AI's context, and allow any arbitrary changes, but beware this uses up more of your AI credits. *Note: Your content after the ${/} will get omitted from the GUI,
but it will be used by the AI.*

* To reference a folder, you can mention `${/folder_name/}` to bring all the files in that folder into the AI's context. Note that this must end with a slash. *Note: The folder content is omitted from the GUI display, but it will be used by the AI.*

* To reference a specific file, you can use `${/file_name}` to bring that file into the AI's context. *Note: The file content is omitted from the GUI display, but it will be used by the AI.*

* To reference a specific `Named Block` you can use `${MyBlock}` to bring that block of code into the AI's context. *Note: The block content is omitted from the GUI display, but it will be used by the AI.* 

To define `MyBlock` from your code you can just wrap some of your code with something like the following, using Python comment syntax for example:

```py
block_begin MyBlock
...
...some python code...
...
block_end
```
