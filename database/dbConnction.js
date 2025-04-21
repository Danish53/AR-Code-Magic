import { Sequelize } from "sequelize";
import { config } from "dotenv";

config();

const sequelize = new Sequelize(
  process.env.DB_NAME, 
  process.env.MYSQL_USER,
  process.env.MYSQL_PASSWORD,
  {
    host: process.env.MYSQL_HOST,
    dialect: "mysql",
  }
);

const dbConnection = async () => {
  try {
    await sequelize.authenticate();
    console.log("Connected to database!"); 
  } catch (err) {
    console.log(
      `Some error occurred while connecting to database: ${err.message}`
    );
  }
};

export { sequelize, dbConnection };
