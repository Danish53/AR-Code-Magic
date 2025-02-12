import { DataTypes } from "sequelize";
import { sequelize } from "../database/dbConnction.js";

const Orders = sequelize.define(
  "orders",
  {
    id: {
      type: DataTypes.INTEGER,
      autoIncrement: true,
      primaryKey: true,
    },
    user_id: {
      type: DataTypes.INTEGER,
      allowNull: false,
    },
    package_id: {
      type: DataTypes.STRING,
      allowNull: false,
    },
    package_name: {
        type: DataTypes.STRING,
        allowNull: false,
      },
    package_price: {
      type: DataTypes.INTEGER,
      allowNull: false,
    },
    package_duration: {
      type: DataTypes.INTEGER,
      allowNull: false,
    },
    order_status: {
      type: DataTypes.STRING,
      allowNull: false,
    },
    payment_id: {
      type: DataTypes.STRING,
      allowNull: false,
    },
    payment_method: {
      type: DataTypes.STRING,
      allowNull: false,
    },
    order_start_date: {
      type: DataTypes.STRING,
      allowNull: false,
    },
    order_end_date: { 
      type: DataTypes.STRING,
      allowNull: false,
    },
    ar_codes:{
        type: DataTypes.STRING,
        allowNull: false
    },
    scans: {
        type: DataTypes.STRING,
        allowNull: false
    },
    pages: {
        type: DataTypes.STRING,
        allowNull: false
    },
    tracking: {
        type: DataTypes.STRING,
        allowNull: false
    }
  },
  {
    timestamps: true,
  }
);

export { Orders };
