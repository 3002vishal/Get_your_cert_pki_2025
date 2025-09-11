require("reflect-metadata");
const express = require('express');
const bodyParser = require('body-parser');
const {AppDataSource} = require('./data-source');

const app = express();
const port = 3000;

app.use(bodyParser.urlencoded({exteneded: true}));
app.set('view engine', 'ejs'); // sets ejs as template so .ejs file can be used from views/.

//--Initialize TypeORM

AppDataSource.initialize()
.then(()=>console.log("Database connnectd wtih TypeORM"))
.catch(err => console.error("DB  connection error:", err));

//--Import routes

const authRoutes = require('./routes/authRoutes');
const certificateRoutes = require('./routes/certificateRoutes');

//--Use routes

app.use('/', authRoutes);
app.use('/' , certificateRoutes);

app.listen(port, () => console.log(`server running at http://localhost:${port}`));
