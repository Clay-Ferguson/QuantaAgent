# About Quanta Agent

This is a tool to automate querying AIs (LLMs) about your codebase. That is, if you're a software developer and you want to be able to ask AI (like OpenAI's ChatGPT for example) questions about very specific parts of your code this tool helps do that. This tool can also implement entire complex features in your code base, using the `Injection Points` capability, mentioned below.

This tool will scan your project and extract named snippets (or sections) of code called `blocks` (i.e. fragments of files, that you identify using structured comments, described below) which are then automatically injected into your prompts (prompt template) by using an assigned name you give to each fragment. 

So in summary let lets you name sections of your code, in any files inside your project, and then refer those sections by name in prompts, in such a way that the prompt injects the code block wherever you mention it's name. So in this way you can write prompts involving sections of your code without the need to cut-and-paste from your code into the prompt by hand.

There's also a way to desginate `Injection Points` anywhere inside these blocks in your actual source files you're analyzing, and the tool will be able to automatically update your code to litterally implement entire features in your code. The `Injection Points` capability is not discussed in this README (to keep it simpler) but you can find full examples (TODO: soon) of `Injection Points` use cases, and associated documentation in the this file `/docs/injection-points.md` 


# Tool Usage Summary

To use this tool you will do these steps:

1) Edit the `config.yaml` to make it point to a software project folder you want to analyze.
2) Put your `OpenAI API Key` in the `config.yaml` (or command line, or env var)
3) Create an empty `data` folder where your output files will go (also in `config.yaml`)
4) Put a `question.md` file (your AI Prompt) into your data folder.
6) Run `main.py`, make up some arbitrary filename when prompted for one.
6) That's it. After running the tool you will have the Question and Answer files saved into your `data` folder based of the filename you specified. If you had `Injection Points` specified in your code that you asked about then your actual software project files will have been updated/edited as well!


# Comparison to other AI Coding Assistants

* Q: How does `Quanta Agent` compare to other `AI Coding Assistants` like Devin, Pythagora (GPT Pilot), and MetaGPT?

* A: `Quanta Agent` is a tiny project that does a more targeted and specific analysis on your software project than the other tools, which results in less API token consumption and therefore lowers Cloud API costs. This is because `Quanta Agent` will only be able to see the parts of your code that you're referencing in your prompt, and it will only try to make modifications in those areas of the code. So not only is `Quanta Agent` very cheap due to using fewer tokens, but you will also get the best possible results from LLMs by keeping your prompts down to where they contain only the exact relevant parts of your codebase. That is, smaller shorter prompts always give the best results. 

`Quanta Agent` is also only for use by actual software developers, rather than a higher level of say a software manager role. This is because `Quanta Agent` expects you to know exactly what parts of your code you need to ask questions about or modify. `Quanta Agent` is like a software developer who needs to be told which parts of the code to look at, before he gets started working. So `Quanta Agent` isn't really for building projects from scratch, but it's more of a tool for making code modifications to large projects that already exist, and making modifications into only the specific allowed bounded areas. Depending on how you look at it, `Quanta Agent` is both dumber than, and smarter than, the other tools. However, I will be so bold as to say there's not a cheaper (in dollar costs) or a simpler way to accomplish what `Quanta Agent` is doing!


# Simple LLM Prompt Example

Suppose you have a Java file that contains the following:

```java
// block.begin Adding_Numbers
int total = a + b;
// block.end
```

You can run run LLM Prompts/Queries like this:

    What is happening in the following code:

    ${Adding_Numbers}

So you're basically labeling (or naming) arbitrary sections of your code (or other text files) in such a way that this tool can build queries out of templates that refrence the named blocks of code. You can go anywhere in your codebase and wrap sections of code with this `block.begin` and `block.end` syntax, to create named blocks which are then template substituded automatically into your prompt.

# Simple Example Files

Example Question and Answer(s) can be found here:

https://github.com/Clay-Ferguson/QuantaAgent/tree/master/data

## Supported syntax

Choose any syntax based on file type. For example Python uses "#", JavaScript/Java uses "//", SQL uses "--"

```txt
// block.begin ...
// block.end

-- block.begin ...
-- block.end

# block.begin ...
# block.end
```


# Background and Inspiration

There are other coding assistants like Github's Copilot for example, which let you ask arbitrary questions about your codebase, and those tools are very useful. However `Quanta Agent` lets you ask AI questions (i.e. build prompts) in a more flexible, targeted, specific, and repeatable way, and automatically saves the history of all your query outputs into markdown text files. `Quanta Agent` can solve more complex and difficult questions, in a repeatable way that doesn't require lots of developer time spent in building the same (or similar) prompts over and over again.

For example, let's say you have some SQL in your project and some Java Entity beans that go along with your database tables. You might want to be able to alter or add SQL tables and/or automatically create the associated Java Entity beans. To get AI to do this for you, in a way that "fits into" your application architecture perfectly, you would want to create prompts that show examples of how you're doing each of these types of artifacts (the SQL and the Java), and then ask the AI to generate new code following that pattern. `Quanta Agent` helps you build these kinds of complex prompts, and keeps developers from having to construct these prompts manually.


# How it Works (Identifying Blocks)

In summary `Quanta Agent` allows you to define named blocks inside any of you files like this:

```sql
-- block.begin SQL_Scripts
...all the scripts
-- block.end 
```

--or--

```java
// block.begin My_Java
...all the code
// block.end 
```

and then use the named blocks in AI prompts, to insert the entire content of the block from the file. The text that comes after the `block.begin` is considered the `Block Name` and, as shown in the example above, the `Block Names` are usable in prompts. So `${SQL_Scripts}` and `${My_Java}` when used in a prompt will be replaced with the block content in the final prompt sent to the LLM.

Note: If only `block.begin` exists and `block.end` doesn't exist, the block will end at the end of the file.

Note: The relative filename is also a valid "block name" and will insert the entire content of the specified file into the prompt. So you can simply put `${/path/to/my/file.md}` in a prompt, and it will inject the entire content of the file into the prompt. Note that the configured `source_folder` is the assumed prefix (base folder) for all of these kinds of file names.

So, in summary, The tool will scan all your source files (inside `source_folder`) and collect all these "Named Blocks" of code, and then you can just use the names themselvels in your prompts templates, to inject the block content.



# Use Cases

## Code Generation

You can use `Blocks` to give specific examples of how your software project architectue does various different things, and then ask the AI to create new objects, code, features, or SQL, or anything else that follows the examples from your own app, so it's much easier to get AI go generate code for you that's fine tuned just for your specific code base.

## Finding Bugs or Getting Recommendations

You can specify `Blocks` or entire files, in your prompt template, and then ask the AI to simply make recommendations of improvements or find bugs.

## New Employee Training

If you decorate specific sections (or blocks) of your company's codebase with these kinds of named blocks, then you can write prompts that are constructed to ask a question about a set of `blocks` that will be super inforformative to new employees learning the codebase, and able to be very specific questions about architecture that really cannot be replicated with tools like Github Copilot.

## Adding new Features or Altering Code

The hard part about adding new features to most codebases is remembering all the different locations in the codebase that might need to be altered in order to get the new feature working, and because every app is a little bit different, a tool like this is really the only way to have prompts that are good enough to make complex changes, that would otherwise require a true AGI. For example, if you need to add a new feature, it might require a new Button on the GUI, new POJOs, new SQL, new API calls, etc. So with a tool like `Quanta Agent` you can sort of package up a prompt that grabs from all these various parts of a codebase to perhaps show an example of how one feature is done, just including precisely only the relevent chunks of code, and then do a prompt like "Using all the example code as your architectural example to follow, create a new feature that does ${feature_description}." So the context for all the aforementioned example code would just be build using the code chunks from various snippets all around the codebase.

## Code Reviews

Developer teams could theoretically use a standard where (perhaps only temporarily) specific block names are required to be put in the code around all changes or specific types of changes. Then you can use AI to run various kinds of automated code reviews (security audits, code correctness audits, AI suggestions for improvements) that specifically look at all the parts of the code involved in any but fix or new feature.


# Configuration and Usage Flow

To run this tool, you should create some data folder and then point the `/config/config.yaml data_folder` to that folder location. This folder will be where the input (the LLM Prompt) is read from and also where the output (AI Generated Responses) are written to. For ease of use in this prototype app we just always expect the prompt itself to be in `${data_folder}\question.md`. So when you run this app it assumes that you have created a file named `question.md` that contains your prompt. As you edit your `question.md` file and then run the tool to generate answers you don't need to worry about maintaining a history of the questions, becasue they're all stored as part of the output. So you can just resave your next question.md file before you run the tool, and it's a fairly good user experience. This app will eventually have a GUI and/or an HTTP API, but for now feeding in prompts via question.md file is idea..

When you run this app, first all your source is scanned (i.e. `source_folder` config property), to build up your named blocks of code. Then your `question.md` file is read, and all the template substitutions are made in it (leaving the `question.md` itself as is), and then the call to OpenAI is made to generate the response. The response file is then written into the output folder, in a timestamped file, so you will have your entire history of questions & answers saved permanently in your `data_folder`.

An example `data_folder` (named `data` in the project root) is included in this project so you can see examples, to get a better more undersanding of how this tool works.


# Project Setup Tips (Development Environment)

## Create a conda environment

    We recommend 'conda' but that's optional of course. All that's really required is Python.

    conda create -n quanta_agent python=3.11.5
    conda activate quanta_agent

    Don't forget to activate your "quanta_agent" environment in your IDE. IDE's, like VSCode, require you to choose the
    Python interpreter, so simply running 'conda activate quanta_agent' won't be enough.

# Configs

The current `config.py` will automatically find the API keys from `..\secrets\secrets.yaml`, and it's not recommended to put them directly into config.yaml itself, because of risk of accidental commits to github


# Future Features

Improvements being considered, but not yet being worked on are as follows:

## Code Injection Points

We could allow a way to have `Code Injection Points` which are defined blocks in your code where the tool can be instructed to allow the AI to generate code to append into those slots. This would allow for a more structured and automatic way for the AI to directly update your project's files, rather than generating a single response file containing instructions on what to add and where to add it.

## Entire Folders as Blocks

We could allow a syntax like `${/my/folder/name}` to be able to inject the entire content of a directory into a prompt. This would rarely be needed, and would be expensive in terms of flooding the AI context window.


# Notes:

* This project is being developed on Python 3.11.5, and on Linux, but afaik it will run on any other platform with Python.


# Resources

https://python.langchain.com/docs/get_started/introduction/

https://python.langchain.com/docs/integrations/chat/openai/
