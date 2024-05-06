# Injection Points

## Purpose

The purpose of `Injection Points` is to give this AI agent the ability to automatically make complex and detailed changes to your codebase! You just tell the AI what to do, and it goes off and implements the code changes directly in your software projects!

It's best to describe `Injection Points` using a simple example. We'll do an example involving one Java file, and a trivial requested refactoring of it. 

## Define Injection Point(s) in Source Code

Let's say we have a Java file named `UserAccount.java` in our project (i.e. somewhere in the `cfg.source_folder` path) and it contains this:

```java
@Entity
@Table(name = "user_accnt")
public class UserAccount {
    // block.inject UserAccount.Properties

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

    // block.inject UserAccount.Methods

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    ...other getters/setters omitted
}
```

Note that there are two defined injection points (lines with `// block.inject {name}`) in the file that we've added so this tool can edit the file for us. We can use whatever `{name}` we want as long as each name is unique across the entire project. 

## Prompt File

Now we're going to put in our `/data/question.md` file the following (the content between *BEGIN* and *END*), which will be the Prompt (actually a template of a prompt) to the AI:

*BEGIN*

Here's an example of an entity bean in my app:

```java
${/main/java/quanta/postgres/table/UserAccount.java}
```

Add the changes to my entity bean for a new User Account property called "signupDate", which will be a date type. 

*END*

## About the above Prompt File

In this case we're referencing the entire Java file by it's filename. You can also reference any `Named Blocks` by name if you don't want to pull in the whole file, but in this case we want the whole file included in our prompt, so we don't use `Named Blocks`. So we're basically just running a prompt that involves the whole file.

The net result of running that prompt above is that your project file(s) will be updated with exactly what you asked the AI to do! 

## Run the Tool

Now we just run the `main.py`. It will prompt us to enter a filename which is basically only so you can give this agent request a name for finding its logs in your data folder. We'll enter `add-signup-date` as our filename, and hit enter to let the tool run. The tool will analyze our project, make a call to the AI, and then since we have `Injection Points` in this case, it will update our project files as it sees fit, into the various injection points as it sees fit. You've requested for a new feature to be added and an AI Software Engineer/Agent made the change for you directly into your code!

## Results the Tool Accmplished

After running the tool, which we just did, our UserAccount.java file will have been edited by the Agent and will now contain the following:

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

// block.inject UserAccount.Imports
// inject.begin 1714886674112
import jakarta.persistence.Temporal;
import jakarta.persistence.TemporalType;
import java.util.Date;
// inject.end

@Entity
@Table(name = "user_accnt")
public class UserAccount {
    
    // block.inject UserAccount.Properties
    // inject.begin 1714886674112
    @Column(name = "signup_date")
    @Temporal(TemporalType.DATE)
    private Date signupDate;
    // inject.end

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

    // block.inject UserAccount.Methods
    // inject.begin 1714886674112
    public Date getSignupDate() {
    return signupDate;
    }

    public void setSignupDate(Date signupDate) {
    this.signupDate = signupDate;
    }
    // inject.end

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }
    ...other getters/setters omitted
}
```

Note that the `inject.begin` and `inject.end` lines indicate exactly where the tool inserted stuff into your code along with a timestamp for auditing purposes. This will be made optional, but for now is always there.

## Prompt Input/Output Logs

To see the actual AI Question and Answer files that were used to accomplish the above, there's a copy of them here, in this project. The tool always generates these two files using the name you entered when you ran the tool. There is a question file and an answer file (--Q.md and --A.md)

https://github.com/Clay-Ferguson/QuantaAgent/tree/master/data/add-signup-date--Q.md

https://github.com/Clay-Ferguson/QuantaAgent/tree/master/data/add-signup-date--A.md


So in addition to just looking into your project to see what files changed, you can get the full explanation of it as well from the `*--A.md` file (A is for Answer), which for the case above example, contains this (between *BEGIN* and *END*).

*BEGIN*

To add the new `signupDate` property to your `UserAccount` entity, you will need to make changes in the imports section, properties section, and methods section. Here are the necessary additions:

1. **Imports Section** - for the date handling.
2. **Properties Section** - to define the new `signupDate` property.
3. **Methods Section** - to add getter and setter methods for `signupDate`.

Here are the changes you should inject into each respective block:

```java
// inject.begin UserAccount.Imports
import jakarta.persistence.Temporal;
import jakarta.persistence.TemporalType;
import java.util.Date;
// inject.end

// inject.begin UserAccount.Properties
@Column(name = "signup_date")
@Temporal(TemporalType.DATE)
private Date signupDate;
// inject.end

// inject.begin UserAccount.Methods
public Date getSignupDate() {
    return signupDate;
}

public void setSignupDate(Date signupDate) {
    this.signupDate = signupDate;
}
// inject.end
```

These snippets should be placed into the respective sections of your `UserAccount` entity code, where the `block.inject` comments are located. This will effectively add the new `signupDate` property to your entity.


____________________________________________________________________________________
Note: The above content is the response from OpenAI's API using the following prompt:

OpenAI Model Used: gpt-4-turbo-2024-04-09

System Prompt: You are a helpful assistant.

Timestamp: 1714886674112

User Prompt: [omitted, you saw it above]

*END*

As you can see, it gave the full description of what happened, and what it put into each `Injection Point` of your code. You can ignore the `inject.begin` and `inject.end` because those tags were what the AI was instructed to put in it's answer to make the answer machine parsable, which is how this tool knows what to insert in your code and where. The timestamp is inserted as the same timestamp across all modifications for any given run of this tool, so there's a full audit trail for everything that ever happens!

## Summary

So this was just a simple code change that was requested, but if you have a large software project, you can write prompts to accomplish virtually any type of code modification you want involving multiple files. For example, if I had wanted the AI to also update my SQL files to go along with adding the new `date` property from the example, all I would've needed to do was reference a `Block Name` or `File Name` in my `question.md` prompt, and as long as my mentioned SQL file (or named block) and had an `Injection Point` defined anywhere in it the tool would've made not only the changes to the Java but also the correct associated SQL ALTER TABLE command in the SQL file too!

## Q & A

* Q: Does this mean I need to put thousands of `Injection Points` everywhere in my code to use this tool?
* A: No! When you're going to make a code refactoring using this tool, all you have to do is figure out *where* you want the actual inserts to take place, and go insert just an injection point at those places. The AI still does all the hard part of figuring out what code to write.

* Q: Do I need to use any `Injection Points` at all to use this tool?
* A: Nope. You can simply refer to `Named Blocks` or `Files` in your question.md file and ask questions about your code and the output responses will be generated into your `data` folder, and none of your files will be altered in any way.

* Q: Are `Injection Points` supposed to be permanent? They're gonna get ugly at scale.
* A: They don't need to be permanant if you don't want. You can just put them in right before you request a new feature, sort of like you were making notes in the code to show an actual human developer where to make some changes, and then after the changes have been made you can delete the notes (Injection Points)