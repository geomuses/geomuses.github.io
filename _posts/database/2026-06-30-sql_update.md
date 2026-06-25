---
layout: post
title:  sql update
date:   2026-06-30 09:01:00 +0800
image: 09.jpg
tags: 
    - sql
    - database
---

```sql
UPDATE table_name
SET column1 = value1, column2 = value2, ...
WHERE condition; 
```

```bash
Alfreds Futterkiste 	Maria Anders 	Obere Str. 57 	Berlin 	12209 	Germany
```


```sql
UPDATE Customers
SET ContactName = 'Alfred Schmidt', City= 'Frankfurt'
WHERE CustomerID = 1;
```

这样就基于`set`把内容给修改了

```bash
Alfreds Futterkiste 	Alfred Schmidt 	Obere Str. 57 	Frankfurt 	12209 	Germany
```