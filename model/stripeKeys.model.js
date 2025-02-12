import { DataTypes } from "sequelize";
import { sequelize } from "../database/dbConnction.js";

const StripeKeys = sequelize.define(
  "stripeKeys",
  {
    id: {
      type: DataTypes.INTEGER,
      autoIncrement: true,
      primaryKey: true,
    },
    stripe_client_id: {
      type: DataTypes.STRING,
      allowNull: false,
    },
    stripe_secret: {
      type: DataTypes.STRING,
      allowNull: false,
    },
    stripe_status: {
      type: DataTypes.STRING,
      allowNull: false,
    },
  },
  {
    timestamps: true,
  }
);

export { StripeKeys };
