import { DataTypes } from "sequelize";
import { sequelize } from "../database/dbConnction.js";

const ScanLog = sequelize.define("scanlogs", {
  id: {
    type: DataTypes.INTEGER,
    autoIncrement: true,
    primaryKey: true,
  },
  custom_page_id: {
    type: DataTypes.INTEGER,
    allowNull: false,
  },
  device: {
    type: DataTypes.STRING,
  },
  browser: {
    type: DataTypes.STRING,
  },
  os: {
    type: DataTypes.STRING,
  },
  ip_address: {
    type: DataTypes.STRING,
  },
  country: {
    type: DataTypes.STRING,
  },
  city: {
    type: DataTypes.STRING,
  }
}, {
  timestamps: true,
});

export { ScanLog };
