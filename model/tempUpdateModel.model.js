import { DataTypes } from "sequelize";
import { sequelize } from "../database/dbConnction.js";

const UpdateModel = sequelize.define(
  "UpdateModel",
  {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true,
    },
    user_id: {
      type: DataTypes.UUID,
      allowNull: false,
    },
    type_name: {
      type: DataTypes.STRING,
      allowNull: false,
    },
    model_path: {
      type: DataTypes.STRING,
    },
  },
  {
    timestamps: true,
  }
);

export { UpdateModel };
