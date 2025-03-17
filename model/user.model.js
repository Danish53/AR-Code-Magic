import { DataTypes } from "sequelize";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";
import { sequelize } from "../database/dbConnction.js";

const Users = sequelize.define(
  "users",
  {
    id: {
      type: DataTypes.INTEGER,
      autoIncrement: true,
      primaryKey: true,
    },
    user_name: {
      type: DataTypes.STRING,
      allowNull: false,
      unique: true,
    },
    email: {
      type: DataTypes.STRING,
      allowNull: false,
      unique: true,
      validate: {
        isEmail: true,
      },
    },
    role: {
      type: DataTypes.ENUM("admin", "user"),
      allowNull: false,
      defaultValue: "user",
    },
    password: {
      type: DataTypes.STRING,
      allowNull: false,
    },
    profileAvatar: {
      type: DataTypes.STRING,
    },
    otp: {
      type: DataTypes.STRING,
    },
    expires_at: {
      type: DataTypes.DATE,
      defaultValue: null,
    },
    isTrial: {
      type: DataTypes.INTEGER,
      allowNull: false,
      defaultValue: 0,
    }
  },

  {
    hooks: {
      beforeCreate: async (user) => {
        if (user.password) {
          const salt = await bcrypt.genSalt(10);
          user.password = await bcrypt.hash(user.password, salt);
        }
      },
      beforeUpdate: async (user) => {
        if (user.password && user.changed("password")) {
          if (user.role !== "admin") {
            const salt = await bcrypt.genSalt(10);
            user.password = await bcrypt.hash(user.password, salt);
          }
        }
      },
    },
    timestamps: true,
  }
);

Users.prototype.comparePassword = async function (enteredPassword) {
  return await bcrypt.compare(enteredPassword, this.password);
};

Users.prototype.getJWTToken = function () {
  return jwt.sign( 
    { id: this.id, email: this.email },
    process.env.JWT_SECRET_KEY,
    {
      expiresIn: process.env.EXPIRES_jWT || "1d",
    }
  );
};

export { Users };
