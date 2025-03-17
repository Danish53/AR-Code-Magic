import { sequelize } from "../database/dbConnction.js";
import { Packages } from "./packages.model.js";
import { Users } from "./user.model.js";
import { AdminSettings } from "./settings.model.js";
import { blogCategories } from "./blogCategories.model.js";
import { blogs } from "./blogs.model.js";
import { Orders } from "./orders.model.js";
import { StripeKeys } from "./stripeKeys.model.js";
import { ArTypes } from "./arTypes.model.js";
import { UpdateModel } from "./tempUpdateModel.model.js";

Users.hasMany(Packages, {
  foreignKey: "added_by",
  as: "packages",
});
Packages.belongsTo(Users, {
  foreignKey: "added_by",
  as: "users",
});
Users.hasMany(ArTypes, {
  foreignKey: "user_id",
  as: "artypes",
});
ArTypes.belongsTo(Users, {
  foreignKey: "user_id",
  as: "users",
});

export { sequelize, Users, Packages, AdminSettings, blogCategories, blogs, Orders, StripeKeys, ArTypes, UpdateModel };
