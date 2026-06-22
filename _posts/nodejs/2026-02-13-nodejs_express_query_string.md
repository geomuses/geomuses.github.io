---
layout: post
title:  nodejs express query string
date:   2026-02-13 09:01:00 +0800
tags: 
    - nodejs
image: 16.jpg
---

```js
const express = require('express');
const app = express();

app.get('/', (req, res) => {
    res.send('Hello World');
});

app.get('/user', (req, res) => {
    const city = req.query.city;
    res.send('city: '+city);
});

app.listen(3000, () => {
    console.log('Server is running on port 3000');
});
```

输入 

```bash
http://127.0.0.1:3000/user?city=taipiei
>>> city: taipiei
```