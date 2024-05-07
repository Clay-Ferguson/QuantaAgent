# About Quanta Agent

This is a tool to automate querying AIs (LLMs) about your codebase. That is, if you're a software developer and you want to be able to ask AI (like OpenAI's ChatGPT for example) questions about very specific parts of your code this tool helps do that. This tool can also implement entire complex features in your code base, using the `Injection Points` capability, mentioned below, to add code to specific locations in specific files as directed by you. In addition to `Injection Points` you can use the simpler approach of referring to files by name in your prompt (using `${/my/file.md}` syntax) and request for the AI to make modifications directly to those files and make arbitrary code refactorings that you ask for in your prompt!

This tool will [optionally] scan your project and extract named snippets (or sections) of code called `blocks` (i.e. fragments of files, that you identify using structured comments, described below) which are then automatically injected into your prompts (prompt template) by using an assigned name you give to each fragment. 

So in summary let lets you name sections of your code, in any files inside your project, and then refer those sections by name in prompts, in such a way that the prompt injects the code block wherever you mention it's name. So in this way you can write prompts involving sections of your code without the need to cut-and-paste from your code into the prompt by hand, and without referencing the entire file in your prompt (which causes the entier file to be included in the prompt)

There's also a way to desginate `Injection Points` anywhere inside the source folder structure you're working with, and the tool will be able to automatically update your code to litterally implement entire features in your code. The `Injection Points` capability is not discussed in this README, but you can find full examples of `Injection Points` use cases, and associated documentation in the this file `/docs/injection-points.md` 


# Simplest Possible Example

The simplest possible example (to put in `question.md` as your prompt) would be this:

```txt
Modify the following Python file, so that it's using a class that has a public static `run` method to do what it does.

${/temperature_convert.py}
```

In the above prompt we're using the syntax to inject the entire `temperature_convert.py` file into the prompt, and the tool is smart enough to actually *do* what you're asking *to* the actual file when you run the tool! The default `config.yaml` already points to the `test_project` folder, which does contain a `temperature_convert.py` which is not implemented as a class. So running this example will update the actual python file and make it into a class.

Note 1: that the above example didn't use `Code Blocks` or `Injection Points` features, which are more advanced features. The simplest way to use the tool is to just request a refactoring to be done on one or more files, which is what we did in the above example.

Note 2: The /data/convert-to-class*.md files in this project are the logs generated from an actual run of the above prompt exactly as described.


# Tool Usage

To use this tool you will do these steps:

1) Edit the `config.yaml` to make it point to a software project folder you want to analyze, and other options.
2) Put your `OpenAI API Key` in the `config.yaml` (or command line, or env var)
3) Create an empty `data` folder where your output files will go (also in `config.yaml`)
4) Put a `question.md` file (your AI Prompt) into your data folder.
5) Run `main.py`, make up some arbitrary filename when prompted for one.
6) That's it. After running the tool you will have the Question and Answer files saved into your `data` folder based of the filename you specified. If you had `Injection Points` specified in your code that you asked about then your actual software project files will have been updated/edited as well!

### update_strategy Option

NOTE: The default config setting for the `update_strategy` config option is `whole_file` (not `injection_points`). When you run the tool you have to set this option to tell it whether it should try to update files based on `Injection Points` (explained later) or `Whole Files`. The `whole_file` option lets you ask the AI to essentially edit one or more files for you and it will overwrite your existing file(s) with new content as it sees fit based on what you asked it to do in your prompt.

# Comparison to other AI Coding Assistants

* Q: How does `Quanta Agent` compare to other `AI Coding Assistants` like Devin, Pythagora (GPT Pilot), and MetaGPT?
* A: `Quanta Agent` is a tiny project that does a more targeted and specific analysis on your software project than the other tools, which results in less API token consumption and therefore lowers Cloud API costs. This is because `Quanta Agent` will only be able to see the parts of your code that you're referencing in your prompt, and it will only try to make modifications in those areas of the code. So not only is `Quanta Agent` very cheap due to using fewer tokens, but you will also get the best possible results from LLMs by keeping your prompts down to where they contain only the exact relevant parts of your codebase. That is, smaller shorter prompts always give the best results. 

`Quanta Agent` is also only for use by actual software developers, rather than a higher level of say a software manager role. This is because `Quanta Agent` expects you to know exactly what parts of your code you need to ask questions about or modify. `Quanta Agent` is like a software developer who needs to be told which parts of the code to look at, before he gets started working. So `Quanta Agent` isn't really for building projects from scratch, but it's more of a tool for making code modifications to large projects that already exist, and making modifications into only the specific allowed bounded areas. Depending on how you look at it, `Quanta Agent` is both dumber than, and smarter than, the other tools. However, I will be so bold as to say there's not a cheaper (in dollar costs) or a simpler way to accomplish what `Quanta Agent` is doing!


# Simple LLM Prompt Example

Suppose you have a Java file that contains the following:

```java
// block_begin Adding_Numbers
int total = a + b;
// block_end
```

You can run run LLM Prompts/Queries like this:

    What is happening in the following code:

    ${Adding_Numbers}

So you're basically labeling (or naming) arbitrary sections of your code (or other text files) in such a way that this tool can build queries out of templates that refrence the named blocks of code. You can go anywhere in your codebase and wrap sections of code with this `block_begin` and `block_end` syntax, to create named blocks which are then template substituded automatically into your prompt.

# Simple Example Files

Example Question and Answer(s) can be found here:

https://github.com/Clay-Ferguson/QuantaAgent/tree/master/data

## Supported syntax

Choose any syntax based on file type. For example Python uses "#", JavaScript/Java uses "//", SQL uses "--"

```txt
// block_begin ...
// block_end

-- block_begin ...
-- block_end

# block_begin ...
# block_end
```


# Background and Inspiration

There are other coding assistants like Github's Copilot for example, which let you ask arbitrary questions about your codebase, and those tools are very useful. However `Quanta Agent` lets you ask AI questions (i.e. build prompts) in a more flexible, targeted, specific, and repeatable way, and automatically saves the history of all your query outputs into markdown text files. `Quanta Agent` can solve more complex and difficult questions, in a repeatable way that doesn't require lots of developer time spent in building the same (or similar) prompts over and over again.

For example, let's say you have some SQL in your project and some Java Entity beans that go along with your database tables. You might want to be able to alter or add SQL tables and/or automatically create the associated Java Entity beans. To get AI to do this for you, in a way that "fits into" your application architecture perfectly, you would want to create prompts that show examples of how you're doing each of these types of artifacts (the SQL and the Java), and then ask the AI to generate new code following that pattern. `Quanta Agent` helps you build these kinds of complex prompts, and keeps developers from having to construct these prompts manually.


# How it Works (Identifying Blocks)

In summary `Quanta Agent` allows you to define named blocks inside any of you files like this:

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

and then use the named blocks in AI prompts, to insert the entire content of the block from the file. The text that comes after the `block_begin` is considered the `Block Name` and, as shown in the example above, the `Block Names` are usable in prompts. So `${SQL_Scripts}` and `${My_Java}` when used in a prompt will be replaced with the block content in the final prompt sent to the LLM.

Note: If only `block_begin` exists and `block_end` doesn't exist, the block will end at the end of the file.

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

* **Entire Folders as Blocks** - We could allow a syntax like `${/my/folder/}` to be able to inject the entire content of a directory into a prompt. This would rarely be needed, and would be expensive in terms of flooding the AI context window. However, once LLMs are powerful and cheap enough this feature would let you sort of use your *entire* code base in a single prompt, and also get the AI to make modifications into any file at all as long as there's an `Injection Point` wherever you want new code to go in.
* **HTTP API** - It would be nice if we could call this tool via an HTTP API in addition to the command line, so it can be built into web apps.
* **VSCode Plugin** - We will be adding a VSCode plugin to go along with this tool, which will let you right click any file in and simply type in a kind of refactoring you'd like to do to the file, and get the chagnes made directly to your file itself.


# Resources

https://python.langchain.com/docs/get_started/introduction/

https://python.langchain.com/docs/integrations/chat/openai/
