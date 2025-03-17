import { DataTypes, STRING } from "sequelize";
import { sequelize } from "../database/dbConnction.js";

const ArTypes = sequelize.define(
  "artype",
  {
    // id: {
    //   type: DataTypes.INTEGER,
    //   autoIncrement: true,
    //   primaryKey: true,
    // },
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true,
    },
    type_name: {
      type: DataTypes.STRING,
      allowNull: false,
    },
    ar_type: {
      type: DataTypes.STRING,
      // allowNull: false,
    },
    font: {
      type: DataTypes.STRING,
    },
    color: {
      type: DataTypes.STRING,
    },
    depth: {
      type: DataTypes.FLOAT,
    },
    gloss: {
      type: DataTypes.FLOAT,
    },
    scale: {
      type: DataTypes.FLOAT,
    },
    orientation: {
      type: DataTypes.STRING,
    },
    reference_name: {
      type: DataTypes.STRING,
      allowNull: false,
    },
    content: {
      type: DataTypes.TEXT,
      validate: {
        len: [0, 40],
      },
    },
    url: {
      type: DataTypes.STRING,
    },
    password: {
      type: DataTypes.STRING,
    },
    tracking_pixel: {
      type: DataTypes.STRING,
    },
    custom_page: {
      type: DataTypes.STRING,
    },
    user_id: {
      type: DataTypes.INTEGER,
      references: {
        model: "users",
        key: "id",
      },
    },
    qr_code: {
      type: DataTypes.STRING,
    },
    model_path: {
      type: DataTypes.STRING,
    },
  },
  {
    timestamps: true,
  }
);

export { ArTypes };
