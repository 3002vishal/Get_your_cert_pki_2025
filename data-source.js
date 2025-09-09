const { DataSource } = require("typeorm");

const AppDataSource = new DataSource({
  type: "mysql",                 // database type
  host: "localhost",             // database host
  port: 3306,                    // default MySQL port
  username: "root",              // MySQL username
  password: "Gate2025@",         // MySQL password
  database: "pkia",              // your database name
  synchronize: true,             // auto-create tables (disable in production)
  logging: true,                 // log SQL queries
  entities: [__dirname + "/entity/*.js"], // entity folder
});

module.exports = { AppDataSource };
