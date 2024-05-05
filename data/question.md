Below are my postgres table definitions. 

```sql
${postgres_tables}
```

Here's an example of an entity bean in my app:

```java
${/main/java/quanta/postgres/table/UserAccount.java}
```

Given this information, so you understand my app, show me the SQL `alter table` command, and the changes to my entity bean, if I wanted to add a new User Account property called "signupDate", which will be a date type. 

In your reply please wrap the SQL changes inside a section like this:

SQL-begin
...all your SQL
SQL-end

To provide me with the new code, use the following strategy: Notice that there are sections named `// block.inject {Name}` in the code I gave you. I'd like for you to show me just what I need to insert into each of those `block.inject` sections of the code. So when you show code, show only the changes and show the changes like this format in your response:

block.inject.begin {Name}
...{SomeContent}...
block.inject.end

You may not need to inject into some of the `block.inject` locations. These `block.inject` points are just for you to refer to which places the code needs to be inserted, and to provide it back to me in a machine parsable way.