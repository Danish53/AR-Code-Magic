import { DataTypes } from "sequelize";
import { sequelize } from "../database/dbConnction.js";

const blogs = sequelize.define(
  "blogs",
  {
    id: {
      type: DataTypes.INTEGER,
      autoIncrement: true,
      primaryKey: true,
    },
    blog_category: {
      type: DataTypes.STRING,
    },
    blog_title: {
      type: DataTypes.STRING,
    },
    blog_image: {
      type: DataTypes.STRING,
    },
    short_description: {
      type: DataTypes.STRING,
    },
    long_description: {
      type: DataTypes.STRING,
    },
  },
  {
    timestamps: true,
  }
);

export { blogs };
