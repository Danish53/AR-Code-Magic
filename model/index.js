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
import { CustomPage } from "./customPages.model.js"
import { TrackingPixel } from "./trackingPixel.model.js"
import { ScanLog } from "./scanLog.model.js"
import { TeamMember } from "./teamMembers.model.js"

Users.hasMany(Packages, {
  foreignKey: "added_by",
  constraints: false,
  as: "packages",
});
Packages.belongsTo(Users, {
  foreignKey: "added_by",
  constraints: false,
  as: "users",
});
Users.belongsTo(Packages, {
  foreignKey: "package_id",
  constraints: false,
  as: "plan",
});
Users.hasMany(ArTypes, {
  foreignKey: "user_id",
  constraints: false,
  as: "artypes",
});
ArTypes.belongsTo(Users, {
  foreignKey: "user_id",
  constraints: false,
  as: "users",
});
blogs.belongsTo(blogCategories, {
  foreignKey: "blog_category",
  as: "category",
});

blogCategories.hasMany(blogs, {
  foreignKey: "blog_category",
  as: "blogs",
});




export { sequelize, Users, Packages, AdminSettings, blogCategories, blogs, Orders, StripeKeys, ArTypes, UpdateModel, CustomPage, TrackingPixel, ScanLog, TeamMember };
