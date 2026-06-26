---
layout: post
title:  sql select top
date:   2026-07-02 09:01:00 +0800
image: 09.jpg
tags: 
    - sql
    - database
---

Select only the first 3 records of the Customers table

```sql
SELECT TOP 3 * FROM Customers;
```

same

```sql
SELECT * FROM Customers
LIMIT 3;
```

 Syntax for MySQL

```sql
SELECT column_name(s)
FROM table_name
WHERE condition
LIMIT number;
```