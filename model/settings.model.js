import { DataTypes } from "sequelize";
import { sequelize } from "../database/dbConnction.js";

const AdminSettings = sequelize.define(
  "systemSettings",
  {
    id: {
      type: DataTypes.INTEGER,
      autoIncrement: true,
      primaryKey: true,
    },
    system_name: {
      type: DataTypes.STRING,
      defaultValue: "AR Magic",
    },
    system_logo: {
      type: DataTypes.STRING,
    },
    email: {
      type: DataTypes.STRING,
    },
    address: {
      type: DataTypes.STRING,
    },
    phone: {
      type: DataTypes.STRING,
    },
    facebook: {
      type: DataTypes.STRING,
    },
    instagram: {
      type: DataTypes.STRING,
    },
    twitter: {
      type: DataTypes.STRING,
    },
    linkedin: {
      type: DataTypes.STRING,
    },
    youtube: {
      type: DataTypes.STRING,
    },
  },
  {
    timestamps: true,
  }
);

export { AdminSettings };
