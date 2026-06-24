---
layout: post
title:  sql insert into 
date:   2026-06-28 09:01:00 +0800
image: 09.jpg
tags: 
    - sql
    - database
---

# Insert Data Only

Here we insert values for ALL the columns of the table, so we omit the column names.

```sql
INSERT INTO Customers  
VALUES ('Cardinal', 'Tom B. Erichsen', 'Skagen 21', 'Stavanger', '4006', 'Norway');
```


# Insert Data Only in Specific Columns

Here we insert values only in some specific columns of the table.

```sql
INSERT INTO Customers (CustomerName, City, Country)  
VALUES ('Cardinal', 'Stavanger', 'Norway');
```

# Insert Multiple Rows

```sql
INSERT INTO Customers (CustomerName, ContactName, Address, City, PostalCode, Country)
VALUES
('Cardinal', 'Tom B. Erichsen', 'Skagen 21', 'Stavanger', '4006', 'Norway'),
('Greasy Burger', 'Per Olsen', 'Gateveien 15', 'Sandnes', '4306', 'Norway'),
('Tasty Tee', 'Finn Egan', 'Streetroad 19B', 'Liverpool', 'L1 0AA', 'UK');
```