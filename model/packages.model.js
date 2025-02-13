import { DataTypes } from "sequelize";
import { sequelize } from "../database/dbConnction.js";

const Packages = sequelize.define(
  "packages",
  {
    id: {
      type: DataTypes.INTEGER,
      autoIncrement: true,
      primaryKey: true,
    },
    package_name: {
      type: DataTypes.STRING,
    },
    package_title: {
      type: DataTypes.STRING,
    },
    package_price: {
      type: DataTypes.INTEGER,
    },
    discount_price: {
      type: DataTypes.INTEGER,
    },
    discount: {
      type: DataTypes.INTEGER,
    },
    duration: {
      type: DataTypes.INTEGER,
    },
    plan_frequency: {
      type: DataTypes.INTEGER,
    },
    description: {
      type: DataTypes.STRING,
    },
    scans: {
      type: DataTypes.INTEGER,
    },
    ar_codes: {
      type: DataTypes.INTEGER,
    },
    pages: {
      type: DataTypes.INTEGER,
    },
    tracking: {
      type: DataTypes.INTEGER,
    },
    added_by: {
      type: DataTypes.INTEGER,
      references: {
        model: "users",
        key: "id",
      },
      allowNull: false,
    },
  },
  {
    timestamps: true,
  }
);

export { Packages };
