# Named Blocks

This tool can run in either `blocks` mode or `files` mode (see `README.md` for more info on modes), and this file applies only to when you're running in `blocks` mode.

You can define `Named Blocks` in your code to identify specific areas which you'd like to ask questions about by name (name of a block), to save you from having to continually paste those sections of code into AI prompts.

In other words, this tool will (if in `blocks` mode) scan your project and extract named snippets (or sections of code) called `blocks` (i.e. fragments of files, that you identify using structured comments, described below) which are then automatically injected into your prompts. 

### How it Works (Blocks Syntax)

Named blocks are defined using this kind syntax to wrap part of your files:

```sql
-- block_begin SQL_Scripts
...some sql scripts...
-- block_end 
```

--or--

```java
// block_begin My_Java
...some source code...
// block_end 
```

In the example above, the text that comes after the `block_begin` is considered the `Block Name` and, so that those blocks anywhere in your code, you can now refer to `${SQL_Scripts}` and/or `${My_Java}` in the text of any prompt, and it will be replaced with the block content (actual source). You can also request for those blocks to be refactored and updates by the AI as well.

