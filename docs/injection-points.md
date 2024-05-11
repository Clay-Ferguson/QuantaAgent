# Injection Points

## Purpose

The purpose of `Injection Points` is to give this tool the ability to automatically make complex and detailed changes to your codebase, but only at specified locations. You just tell the AI what to do, and it goes off and implements the code changes directly in your software projects! If you've defined `Injection Points` inside the code you've provided (which is completely optional) then the tool will only inject code into those locations in your project rather than having the freedom to insert any modifications anywhere in any files.

*Note 1: If you want the tool to be able to make edits anywhere in any files you will use the `whole_file` option instead of `injection_points` option, but this document is specifically about the `injection_points` option.*

*Note 2: Injection Points are always additive to your code. Use this feature when you know you're only *adding* new code at specified spots. If you need the AI to edit arbitrary code, it can do that, but you need to use the `whole_file` mode for that, which is mutually exclusive from `injection_points` 

## Simplest Example
 
Suppose you have a Python file somewhere in your project that contains the following:

    # block_begin MyTestBlock
    print("This is a test block")
    # block_inject NewCodeHere
    # block_end

We can run this prompt:

    Add some code that does the same thing as this line but includes a timestamp in the output as well.

    ```py
    ${MyTestBlock}
    ```

The result of running this tool with the above prompt will be that your new content in the file content block will be this:

    # block_begin MyTestBlock
    print("This is a test block")
    # block_inject NewCodeHere
    # inject_begin 1715123264447
    from datetime import datetime
    print(f"This is a test block at {datetime.now()}")
    # inject_end
    # block_end

Note that the `inject_begin` and `inject_end` lines are wrapping the new injected content, and it went in right at the injection point. This was a contrived simple example but it shows the mechanics of asking questions about code, and getting new code generated into only specific specified locations. 

If you have several places inside a file that need to be modified and you want to let the AI do that, you would wrap the entire file in a `block_begin/block_end`, and put as many `block_inject` locations as you want, and the AI will try to insert the correct content into the correct slot. All you really need to do is make sure each slot (i.e. `Injection Point`) has a unique name, and it doesn't even matter what the name is.


## Another Example

Let's say we have a Java file named `UserAccount.java` in our project (i.e. somewhere in the `cfg.source_folder` path) and it contains the following:

```java
@Entity
@Table(name = "user_accnt")
public class UserAccount {
    // block_inject UserAccount.Properties

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // Adding 'unique = true' to the @Column annotation will make the column
    // be defined as unique in the database.
    @Column(name = "mongo_id", nullable = false, unique = true)
    private String mongoId;

    @Column(name = "user_name", nullable = false, unique = true)
    private String userName;

    @OneToMany(mappedBy = "userAccount", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Tran> trans;

    public UserAccount() {
        // JPA requires a default constructor
    }

    public UserAccount(String mongoId, String userName) {
        this.mongoId = mongoId;
        this.userName = userName;
    }

    // block_inject UserAccount.Methods

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    ...other getters/setters omitted
}
```

Note that there are two defined injection points (lines with `// block_inject {name}`) in the file that we've added so this tool can edit the file for us, but will only insert at those locations in the file. We can use whatever `{name}` we want as long as each name is unique across the entire project. 

## Prompt File

Now we're going to put in our `/data/question.txt` the following (the content between *BEGIN* and *END*), which will be the Prompt (actually a template of a prompt) to the AI:

*BEGIN*

Here's an example of an entity bean in my app:

    ${/main/java/quanta/postgres/table/UserAccount.java}
 
Add the changes to my entity bean for a new User Account property called "signupDate", which will be a date type. 

*END*

## Run the Tool

Now we just run the `quanta-agent.py`. It will ask us to enter a filename which is basically only so it can give this agent request a name for finding its logs in your data folder. We'll enter `add-signup-date` as our filename, and hit enter to let the tool run. The tool will analyze our project, make a call to the AI, and then since we have `Injection Points` in this case, it will update our project files as it sees fit, *but only into the specified injection points*. You've requested for a new feature to be added and an AI Software Engineer/Agent made the change for you directly into your code!

## About the Prompt Above

In this case we're referencing the entire Java file by it's filename. You can also reference any `Named Blocks` by name if you don't want to pull in the whole file, but in this case we want the whole file included in our prompt, so we don't use `Named Blocks`.

## Results the Tool Accomplished

After running the tool, our UserAccount.java file will have been edited by the Agent and will now contain the following:

```java
import java.util.List;
import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;

// block_inject UserAccount.Imports
// inject_begin 1714886674112
import jakarta.persistence.Temporal;
import jakarta.persistence.TemporalType;
import java.util.Date;
// inject_end

@Entity
@Table(name = "user_accnt")
public class UserAccount {
    
    // block_inject UserAccount.Properties
    // inject_begin 1714886674112
    @Column(name = "signup_date")
    @Temporal(TemporalType.DATE)
    private Date signupDate;
    // inject_end

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // Adding 'unique = true' to the @Column annotation will make the column
    // be defined as unique in the database.
    @Column(name = "mongo_id", nullable = false, unique = true)
    private String mongoId;

    @Column(name = "user_name", nullable = false, unique = true)
    private String userName;

    @OneToMany(mappedBy = "userAccount", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Tran> trans;

    public UserAccount() {
        // JPA requires a default constructor
    }

    public UserAccount(String mongoId, String userName) {
        this.mongoId = mongoId;
        this.userName = userName;
    }

    // block_inject UserAccount.Methods
    // inject_begin 1714886674112
    public Date getSignupDate() {
    return signupDate;
    }

    public void setSignupDate(Date signupDate) {
    this.signupDate = signupDate;
    }
    // inject_end

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }
    ...other getters/setters omitted
}
```

Note that the `inject_begin` and `inject_end` lines indicate exactly where the tool inserted into your code along with a timestamp for auditing purposes. This will be made optional, but for now is always there.

## Prompt Input/Output Logs

To see the actual AI Question and Answer files that were used to accomplish the above, there's a copy of them here, in this project (named below). The tool always generates these two files using the name you entered when you ran the tool. There is a question file and an answer file (--Q.txt and --A.txt)

* [Question Log File](/data/add-signup-date--Q.txt)
* [Answer Log File](data/add-signup-date--A.txt)


If you have a large software project, you can write prompts to accomplish virtually any type of code modification you want involving multiple files. For example, if I had wanted the AI to also update my SQL files to go along with adding the new `date` property from the example above, all I would've needed to do was reference a `Block Name` or `File Name` (that encapsulated the SQL as well) in my `question.txt` prompt, and the tool would've made not only the changes to the Java but also the correct associated SQL ALTER TABLE command in the SQL file!

