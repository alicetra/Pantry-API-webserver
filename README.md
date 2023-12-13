## Identification of the problem you are trying to solve by building this particular app.
The problem that this application is trying to solve is indeed multi-faceted, but at its core, it’s about efficient pantry management and reducing waste.

**Inventory Management**<br> 
Without a proper inventory system, it’s easy to lose track of what’s in your pantry. This can lead to duplicate purchases, resulting in unnecessary spending and potential waste. An efficient inventory system can help you keep track of what you have, what you need, and when you need it.

**Shopping List Generation**<br> 
A system that generates a shopping list based on items nearing depletion can prevent the inconvenience of running out of essential items. This not only ensures that your pantry is always well-stocked but also aids in effective meal planning.

**Expiration Tracking**<br>
 Keeping track of expiration dates can be a daunting task, especially with a large number of items. The stress and time constraints can make it challenging to manage. An application that alerts you about nearing expiry dates can help in timely consumption or disposal of food items, reducing waste and maintaining a clean pantry.

**Waste Reduction**<br> 
By addressing the above points, the application aims to reduce food waste significantly. Efficient inventory management, timely replenishment of depleted items, and effective meal planning all contribute to minimizing waste.

##  Why is it a problem that needs solving?

The problem of inefficient pantry management and food waste is a significant one that needs solving for several reasons.

**Rising Grocery Prices and Unnecessary Expenditures**<br>
Firstly, in light of rising grocery prices, it’s more crucial than ever to avoid unnecessary expenditures. Duplicate purchases not only strain the budget but also lead to overstocking and potential wastage.  An efficient grocery shopping list that minimizes waste can help users make the most of their resources and save money. “At the moment, annual food inflation is sitting at 7.5 per cent according to the latest figures from the ABS. Leading the price rise is dairy, which has risen to 15.2 per cent in the past 12 months. Breads and cereals aren’t far behind with an annual change of 11.2 per cent.” (ABC News, 2023)

**Impact on Consumption Habits and the Environment**<br>
Secondly, this problem directly impacts our consumption habits. Overbuying leads to overconsumption and waste, which is detrimental to the environment and our health. By having a well-organized list and the used_by route, users can strategically plan their shopping and meals, leading to healthier eating habits and less food waste.“Australia currently creates more than 7.6 million tonnes of food waste each year – enough to fill the Melbourne Cricket Grounds nine times. Around 10 percent of global greenhouse gas emissions come from food produced but wasted. In Australia, this represents 17.5 million tonnes of CO2 each year.” (Foodbank Australia, n.d.)

**Food Safety Concerns**<br>
Thirdly, food safety is another critical aspect. Consuming expired items can lead to health issues. “Consuming expired food can lead to food poisoning, which can cause symptoms such as nausea, vomiting, diarrhoea, and fever. In severe cases, it can even lead to hospitalisation or, unfortunately, death.” (ASC Consultants, n.d.). Therefore, having a feature that alerts the user to these items is essential for maintaining the quality and safety of the food in the pantry.

**Organized Pantry Cleaning**<br>
Additionally, the expired route allows users to clean their pantry in a more organized manner. It provides a list of items that have already expired, enabling users to identify and get rid of these items. This helps reducing the stress and time it takes to clean a pantry. 

The urgency of solving these problems cannot be overstated. By addressing these problems, the application helps users avoid unnecessary purchases, reduce food waste, and ensure the safety of the food they consume. It’s also about promoting a sustainable and healthy lifestyle in a cost-effective manner.It’s a comprehensive solution to a common problem that many people face in their daily lives, and its importance is amplified in these times of rising costs. 


## Why have you chosen this database system. What are the drawbacks compared to others?

PostgreSQL is a popular choice for many developers due to its robust feature set and open-source nature. Here are some of the reasons why PostgreSQL is a good fit for a pantry inventory API project.

**Pros of PostgreSQL**

- Open-source: PostgreSQL, an open-source software, empowers developers with the ability to modify its code according to specific requirements. This can prove to be useful for a custom pantry inventory API project. The flexibility can foster tailored solutions, yielding greater efficiency and versatility.
- Support for structured and unstructured data: A pantry inventory API would likely need to handle a variety of data types, such as text descriptions of items, numerical quantities of items. PostgreSQL’s ability to handle both structured and unstructured data makes it a versatile choice for this project.
- Extensibility: The pantry inventory API might need to store and query data in ways that aren’t supported by standard SQL data types. PostgreSQL’s support for advanced data types, provides the flexibility and ability to handle these scenarios.
- ACID compliance: In a pantry inventory system, it’s crucial that transactions are processed reliably to prevent data inconsistencies (like negative inventory levels of items). PostgreSQL’s full ACID compliance  will ensure that all transactions are processed reliably.
- Handling large amounts of data: As the pantry inventory grows and the number of users increases, the database will need to handle larger amounts of data. PostgreSQL is designed to manage vast amounts of data efficiently, making it a scalable solution for this project.

**Cons of PostgreSQL**

- Complexity: PostgreSQL is a powerful database system with a lot of features, which can make it more complex to set up and manage compared to simpler databases. This could potentially slow down development of this project.
- Performance: While PostgreSQL is highly efficient in handling complex queries and large databases, it might not perform as well as some other databases for simple read-heavy loads. If the pantry inventory API is expected to have very high read only  rates, this could be a concern.
- Resource-intensive: PostgreSQL can be more resource-intensive than lighter-weight databases like SQLite. If the pantry inventory API is expected to run on limited-resource environments, this could be a disadvantage.
- Lack of built-in sharding: PostgreSQL does not support built-in sharding, a technique used to scale databases by splitting data across multiple servers. If the pantry inventory API needs to scale to handle very large databases in the future, this could require additional work to implement.

When comparing PostgreSQL to other database management systems, it’s important to consider the specific needs of the project. For example, NoSQL databases like MongoDB might be more suitable for projects that require flexibility and scalability, while MySQL might offer better performance for read-heavy operations. However, for a project like a pantry inventory API that requires relational data and ACID compliance, PostgreSQL is a strong choice. 

**PostgreSQL vs MySQL** <br> 
MySQL is another popular open-source relational database management system. While MySQL might offer better performance for read-heavy operations, PostgreSQL’s support for a wider array of data types and its full ACID compliance make it a more robust choice for applications that require complex queries and data integrity. For an pantry inventory API, which likely involves relational data and transactions, PostgreSQL’s features cwill be more beneficial.

**PostgreSQL vs MongoDB**<br> 
MongoDB is a NoSQL database known for its flexibility and scalability. It’s a great choice for applications that deal with large volumes of data and require high write loads. However, it lacks the relational capabilities and ACID compliance of PostgreSQL. Given that a pantry inventory API likely requires relationships between different entities (like users to pantries) , PostgreSQL’s relational model would be more suitable.

**PostgreSQL vs SQLite**<br> 
SQLite is a lightweight disk-based database and doesn’t require a separate server process which allows it to consume less resources than PostgreSQL. It’s a good choice for small applications, embedded systems, or local/single-user databases. However, for a web-based API like the pantry inventory project, PostgreSQL’s robustness, security features, and scalability make it a better choice.

In conclusion, while each database system has its strengths and is suited to specific types of projects, PostgreSQL’s robust feature set, reliability, and strong support for relational data and ACID-compliant transactions make it an excellent choice for my project. It provides the necessary capabilities to handle complex queries and maintain data integrity, which are crucial for managing an inventory system. 

## Identify and discuss the key functionalities and benefits of an ORM

Object-Relational Mapping (ORM) is a technique that lets you interact with your database, like you would with SQL. In other words, it’s a way to create, retrieve, update, and delete records from your database, just as you would with SQL. <br>
In the context of a Flask API application, an ORM offers several key functionalities and benefits.

Key Functionalities:

- Abstraction: these tools offer the capability to interact with databases through high-level entities like classes and objects, eliminating the need for direct SQL query composition. This allow you to focus on programming logic over database management.
- Data Manipulation Language (DML) Operations: ORMs enable the execution of Data Manipulation Language (DML) operations such as INSERT, UPDATE, DELETE and SELECT, through object-oriented syntax; this approach proves more intuitive and manageable for developers adept in object-oriented programming.
- Data Definition Language (DDL) Operations: You can utilized ORM systems for performing Data Definition Language (DDL) operations, including table creation, alteration and deletion. Certain ORMs extend their functionality to automating table creation based on your object definitions.
- Transaction Management: Built-in support for managing transactions, which are crucial to sustain data integrity, is provided by ORMs. You can initiate,commit or rollback these transactions with ease; they arm you with the necessary tools to maintain control over your data's consistency and accuracy.
- Associations and Relationships: ORMs facilitate the establishment and management of table relationships, including one-to-one, one-to-many, and many-to-many associations through intuitive object-oriented syntax.
- Inheritance: Some ORMs support the concept of inheritance at the code level and enable you to establish a parent-child class relationship. This relationship can then be reflected in your database.
- Caching: Many ORMs offer a caching layer for the objects they manage. By curtailing the frequency of database hits can result in  enhances performance: it's an efficient tool in speeding up processes.

Key Benefits:

-  Productivity: ORMs can drastically enhance productivity by eliminating the necessity for writing repetitive SQL code.
- Maintainability: Code written with an ORM typically offers enhanced maintainability. It is easier to update and upkeep due to its use of the object-oriented paradigm, a concept that most developers are already familiar with. Additionally, this method enhances readability; because of its structural similarity to everyday programming practices.
- Consistency: The ORM consistently handles database operations, thereby offering a uniform set of functionalities throughout your application. Consequently, this feature simplifies code comprehension and debugging tasks.
- Portability: ORMs, being database-agnostic, enhance code portability. You can switch to a different database system in the future without necessitating a complete rewrite of all your data query and access code.
- Performance Optimizations: ORMs mitigate the risk of SQL injection by parameterizing inputs to SQL queries: this reduces the likelihood of potential attacks. Nonetheless, it remains imperative to validate and sanitize user inputs; these measures are crucial for maintaining robust security protocols.

In the context of Flask, SQLAlchemy is a popular ORM that integrates well with Flask applications. It provides all the benefits mentioned above, making it a good choice for Flask API applications.

