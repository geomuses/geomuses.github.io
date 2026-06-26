---
layout: post
title:  sql delete
date:   2026-07-01 09:01:00 +0800
image: 09.jpg
tags: 
    - sql
    - database
---

```sql
DELETE FROM table_name WHERE condition;
```


```sql
DELETE FROM Customers WHERE CustomerName='Alfreds Futterkiste';
```


```sql
DROP TABLE Customers;
```


| **特性**        | **DELETE FROM Customers;**   | **DROP TABLE Customers;**   |
| ------------- | ---------------------------- | --------------------------- |
| **操作对象**      | 仅删除表中的**数据（行）**              | 删除整个**表结构**及其所有数据           |
| **表结构保留吗？**   | **保留**。表还在，你还可以往里写新数据        | **不保留**。表彻底消失，查无此表          |
| **空间释放**      | 通常不会立即释放表占用的物理空间             | 立即释放该表占用的所有空间               |
| **能回滚（撤销）吗？** | **能**（如果在事务中，可以用 `ROLLBACK`） | **不能**（属于 DDL 操作，隐式提交，无法撤销） |
| **速度**        | 相对较慢（需要逐行删除并记录日志）            | 极快（直接从数据库元数据中抹去）            |
| **SQL 语言分类**  | **DML**（数据操作语言）              | **DDL**（数据定义语言）             |

