import { DataTypes } from "sequelize";
import { sequelize } from "../database/dbConnction.js";

const blogCategories = sequelize.define(
  "blogCategories",
  {
    id: {
      type: DataTypes.INTEGER,
      autoIncrement: true,
      primaryKey: true,
    },
    category_name: {
      type: DataTypes.STRING,
      defaultValue: "ar-magic",
    },
    category_slug: {
      type: DataTypes.STRING,
    },
    category_description: {
      type: DataTypes.STRING,
    },
  },
  {
    timestamps: true,
  }
);

export { blogCategories };
