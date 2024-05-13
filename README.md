# About Quanta Agent 

A tool to automate querying AIs (LLMs) about your codebase, which can also automatically refactor your actual project files, from high level human language instructions of what changes you'd like to make. You can ask the tool anything about your project, ask for any kind of refactoring you'd like to do in your project, or even ask the tool to create entirely new projects all on it's own.

You have the option to use either the **Streamlit-based Web Interface/GUI, or a Command Line** version that reads the prompt from a simple text file.

# Tool Features

* Answers questions about software projects
* Refactor files or entire projects 
* Answers questions specifically about named blocks of your code
* Create new Software Projects based on a description/prompt.

# Project Summary

* Has Streamlit GUI, as well as Command Line version
* Written 100% in Python
* Open Source Python (MIT License)
* Uses Python Langchain giving you flexibility in which LLM you use, including either locally hosted LLMs or Cloud AI Services.

*Note: Current codebase only includes OpenAI connectivity, but with Langchain it's easy to add support for the other Cloud AIs or Local LLMS.*

If you're a software developer and you want to be able to ask AI (like OpenAI's ChatGPT for example) questions about your code, this tool helps do that. This tool can also implement entire complex features in your code base, by updating existing entire files, or by using the `Injection Points` capability, discussed below, to add code to specific locations in specific files as directed by you. 

To ask questions about or request refactorings inside specific files or folders, you simply refer to them by name in your prompt using the following syntax (*folders must end with a slash*):

For Files: `${/my/file.py}`
For Foders: `${/my/project/folder/}`

You can mention specific files and/or folders in your prompt to request AI to make modifications directly to those files and make arbitrary code refactorings that you ask for in your prompt!


# Tool Usage

To use this tool, follow these steps:

1) Edit the `config.yaml` to make it point to a software project folder you want to analyze.
2) Put your `OpenAI API Key` in the `config.yaml` (or command line, or env var)
3) Create an empty `data` folder where your output files will go (also in `config.yaml`)
4) Make sure your `config.yaml` has `update_strategy: "whole_file"` if you want the tool to be free to update any of your files in their entirety, or set `update_strategy: "injection_points"` if you only want the AI to make changes in places you've pre-designated yourself. Obviously the simpler approach is `whole_file`.
5) If you're using the command line version, then put a `question.txt` file (your AI Prompt) into your data folder and run `python3 quanta-agent.py`. Make up any arbitrary filename when prompted for one when the tool runs.
--or--
5) Run the Streamlit-based Web interface with this command: `streamlit run quanta-agent-gui.py`, and just use the app like a chatbot or and agent which can do code refactoring just like an expert software developer!
7) That's it. After running the tool you will have the Question and Answer files saved into your `data` folder based of the filename you specified. If you had requested for any refactorings to have been done then your actual project files will have been updated, to accomplish whatever you asked for.

*Tip: When requesting project refactorings, it's best to be in a clean project version, so that if you don't like the changes the tool made to your code you can roll them back easily, using `git`.


# Advanced Optional Features

*Note: You don't need to understand `Named Blocks` or `Injection Points` to use this app, so if you're just getting started you can skip this section.*

## Named Blocks

You can define `Named Blocks` in your code, to identify specific areas which you'd like to ask questions about by name, to save you from having to continually paste those sections of code into your AI prompts. Here are the docs on [Named Blocks](./docs/named-blocks.md)

## Injection Points

There's also a way to designate `Injection Points` anywhere inside the source folder structure you're working with, and the tool will be able to automatically update your code to implement refactoring. The `Injection Points` capability is not discussed at length in this README, but you can find full examples of `Injection Points` use cases, and associated documentation in the [Injection Points](./docs/injection-points.md) docs. 

*Note: Now that we have the `whole_file` mode (described elsewhere), you would never need to use `Injection Points` feature unless your files are so massive it's too costly to use the `whole_file` approach. The `whole_file` option is a setting that makes the AI aware of entire files or folders (by sending them as part of the final prompt) in a way that it can arbitrarily refactor those files based on your prompts, whereas the `Injection Points` gives you a way to more precisely tell the AI where you'd like it to make changes.*


# Example 1. Trivial Refactoring

The simplest possible refactoring prompt would be something like this:

```txt
Modify the following Python file, so that it's using a class that has a public static `run` method to do what it does.

${/temperature_convert.py}
```

In the above prompt we're using the `${}` syntax to inject the entire `temperature_convert.py` file into the prompt, and the tool will actually *do* what you're asking for to the actual file when you run the tool! In other words this tool will modify your source files if you ask for that. The default `config.yaml` already points to the `test_project` folder, which contains a `temperature_convert.py` which is not implemented as a class. So running this example will update the actual python file and make it into a class as the prompt requested it to do.

Note: The `/data/convert-to-class*.md` files in this project are the logs generated from an actual run of the above prompt exactly as described. There are lots of other examples in the `data` folder.


# Comparison to other AI Coding Assistants

* Q: How does `Quanta Agent` compare to other `AI Coding Assistants` like Devin, Pythagora (GPT Pilot), and MetaGPT?
* A: `Quanta Agent` does a more targeted and specific analysis on your software project than the other tools, which results in less API token consumption and therefore lowers Cloud API costs. This is because `Quanta Agent` will only be able to see the parts of your code that you're referencing in your prompt, and it will only try to make modifications in those areas of the code. So not only is `Quanta Agent` very cheap due to using fewer API tokens, but you will also get the best possible results from LLMs by keeping your prompts down to where they contain only the relevant parts of your codebase. That is, smaller shorter prompts always give the best results. 

`Quanta Agent` is also only for use by actual software developers, rather than a higher level of something like a software manager role. This is because `Quanta Agent` expects you to know exactly what parts of your code you need to ask questions about or modify. `Quanta Agent` is like a software developer who needs to be told which parts of the code to look at, before he gets started working. So `Quanta Agent` isn't really for building projects from scratch, but it's more of a tool for making code modifications to large projects that already exist, and making modifications into only the specific allowed bounded areas.


# More Examples

## Example 2: Ask Question about a Named Block

Suppose you have a Java file that contains the following, somewhere (anywhere) in your project:

```java
// block_begin Adding_Numbers
int total = a + b;
// block_end
```

You can run LLM Prompts/Queries like this:

    What is happening in the following code:

    ${Adding_Numbers}

So you're basically labeling (or naming) specific sections of your code (or other text files) in such a way that this tool can build queries out of templates that reference the named blocks of code. You can go anywhere in your codebase and wrap sections of code with this `block_begin` and `block_end` syntax, to create named blocks which are then template substituded automatically into your prompt.


# Simple Example Output Log Files

Example Question and Answers can be found in this project's [Data Folder](/data)


# Background and Inspiration

There are other coding assistants like Github's Copilot for example, which let you ask arbitrary questions about your codebase, and those tools are very useful. However `Quanta Agent` lets you ask AI questions (i.e. build prompts) in a more flexible, targeted, specific, and repeatable way, and automatically saves the history of all your query outputs into markdown text files. `Quanta Agent` can solve more complex and difficult questions, in a repeatable way that doesn't require lots of developer time spent in building the same (or similar) prompts over and over again.

For example, let's say you have some SQL in your project and some Java Entity beans that go along with your database tables. You might want to be able to alter or add SQL tables and/or automatically create the associated Java Entity beans. To get the tool to do this for you, in a way that "fits into" your specific application's architecture perfectly, you would want to create prompts that show examples of how you're doing each of these types of artifacts (the SQL and the Java), by wrapping an example in a `Named Block`, and then ask the AI to generate new code following that pattern. 

`Quanta Agent` helps you build these kinds of complex prompts, and keeps developers from having to construct these prompts manually, because you can simply surround the relevant pieces and parts of code related to a specific type of application artifact (like your Java Beans, your SQL, etc), and then write prompts that reference those sections by name. This is what `Named Blocks` are for.

Also since Quanta Agent is based on Langchain, it keeps you from being tied to or dependent upon any specific Cloud AI provider, and gives you the option to run local LLMs for it's use as well.


# Use Cases

## Code Generation

You can use `Named Blocks` to give specific examples of how your software project architecture does various different things, and then ask the AI to create new objects, code, features, SQL, or anything else that follows the examples from your own app, so it's much easier to get AI to generate code for you that's fine tuned just for your specific code base.

## Finding Bugs or Getting Recommendations

You can specify `Named Blocks` or entire files, in your prompt template, and then ask the AI to simply make recommendations of improvements or find bugs.

## New Employee Training

If you annotate specific sections (or blocks) of your company's codebase with these kinds of named blocks, then you can write prompts that are constructed to ask a question about a set of `blocks` that will be super informative to new employees learning the codebase, and able to have very specific questions about architecture that really cannot be replicated with tools like Github Copilot.

## Adding new Features or Refactoring Code

One very hard part about adding new features to most codebases is remembering all the different locations in the codebase that might need to be altered in order to get the new feature working, and because every app is a little bit different, a tool like this is really the only way to have prompts that are good enough to make complex changes, that would otherwise require a true AGI. 

For example, if you need to add a new feature, it might require a new Button on the GUI, new POJOs, new SQL, new API calls, etc. With a tool like `Quanta Agent` you can package up a prompt that grabs from all these various parts of a codebase to show the AI an example of how one feature is done, just including precisely only the relevant chunks of code, and then do a prompt like `"Using all the example code as your architectural example to follow, create a new feature that does ${feature_description}."` So the context for all the aforementioned example code would just be built using the code chunks from various snippets all around the codebase.

## Code Reviews

Developer teams can theoretically use a standard where (perhaps only temporarily) specific block names are required to be put in the code around all changes or specific types of changes. Then you can use AI to run various kinds of automated code reviews, security audits, code correctness audits; or even just get AI suggestions for improvement that specifically look at all the parts of the code involved in any bug fix or new feature that has been implemented and idenfified using `Named Blocks`.


# Configuration and Usage Flow

To run this tool, you should create a data folder and then point the `/config/config.yaml data_folder` to that folder location. This folder will be where the input (the LLM Prompt) is read from and also where the output (AI generated responses) are written to. For ease of use in this prototype app, we always expect the prompt itself to be in `${data_folder}\question.txt`. When you run this app it assumes that you have created a file named `question.txt` that contains your prompt. 

As you edit your `question.txt` file and then run the tool to generate answers you don't need to worry about maintaining a history of the questions and answers, because they're all stored as part of the output in the `data_folder` folder. So you can just resave your next question.txt file before you run the tool, and it's a fairly good user experience, even without a GUI. This app will eventually have a GUI and/or an HTTP API, but for now feeding in prompts via `question.txt` file is ideal.

When you run this app, first all your source is scanned (i.e. `source_folder` config property), to build up your named blocks of code. Then your `question.txt` file is read, and all the template substitutions are made in it (leaving the `question.txt` file as is), and then the call to OpenAI is made to generate the response. The response file is then written into the output folder, so you will have your entire history of questions & answers saved permanently in your `data_folder`. If your prompt had requested any code changes then your actual project files will have been automatically edited to accomplish what you asked for.

An example `data_folder` (named `data` in the project root) is included in this project so you can see examples, to get a better undersanding of how this tool works.


# Project Documentation

Be sure to check the  [Docs Folder](/docs) for more information about this project and how to use it.


# Future Plans

Improvements to this tool currently being considered:

* **HTTP API** - It would be nice if we could call this tool via an HTTP API in addition to the command line, so it can be built into web apps.
