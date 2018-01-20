const express = require('express');
const cors = require('cors');

const tubes = require('./src/tubes');
const models = require('./src/models');

const app = express();

app.use(cors());
//
app.use('/', tubes);
app.use('/', models);


app.listen(8080);