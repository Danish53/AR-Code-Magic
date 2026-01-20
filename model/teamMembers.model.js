import { DataTypes } from "sequelize";
import { sequelize } from "../database/dbConnction.js";

const TeamMember = sequelize.define("teammembers", {
  id: {
    type: DataTypes.INTEGER,
    autoIncrement: true,
    primaryKey: true,
  },
  owner_id: {
    type: DataTypes.INTEGER,
    allowNull: false,
  },
  member_id: {
    type: DataTypes.STRING,
    allowNull: false,
  },
  member_email: {
    type: DataTypes.STRING,
    allowNull: false,
  },
  status: {
    type: DataTypes.ENUM("pending", "accepted"),
    defaultValue: "pending",
  },
  permissions: {
    type: DataTypes.JSON,
    defaultValue: {
      arText: false,
      arPhoto: false,
      arPortal: false,
      arLogo: false,
      arCode: false,
      File3D: false,
    },
  },
});

export { TeamMember };