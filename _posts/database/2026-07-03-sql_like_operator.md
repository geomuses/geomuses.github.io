---
layout: post
title:  sql like operator
date:   2026-07-03 09:01:00 +0800
image: 09.jpg
tags: 
    - sql
    - database
---

- A percent sign `%` - represents zero, one, or multiple characters
- A underscore sign `_` - represents a single character

# Syntax

```sql
SELECT * FROM Customers  
WHERE CustomerName LIKE 'a%';
```

# The _ Wildcard

```sql
SELECT * FROM Customers
WHERE city LIKE 'l_nd__';
```


|Symbol|Description|
|---|---|
|%|Represents zero or more characters|
|_|Represents a single character|
|[]|Represents any single character within the brackets *|
|^|Represents any character not in the brackets *|
|-|Represents any single character within the specified range *|
|{}|Represents any escaped character **|

Return all customers that ends with the pattern 'es'

```sql
SELECT * FROM Customers
WHERE CustomerName LIKE '%es';
```

Return all customers starting with either "b", "s", or "p"

```sql
SELECT * FROM Customers
WHERE CustomerName LIKE '[bsp]%';
```

Return all customers starting with "a", "b", "c", "d", "e" or "f"

```sql
SELECT * FROM Customers  
WHERE CustomerName LIKE '[a-f]%';
```
