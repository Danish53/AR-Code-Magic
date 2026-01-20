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
      type: DataTypes.INTEGER, // 🔥 Must match blogCategories.id type
      allowNull: true,
      references: {
        model: "blogCategories", // table name (not variable)
        key: "id",
      },
      onDelete: "CASCADE",
      onUpdate: "CASCADE",
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
