import { Users, AdminSettings, Packages, blogCategories, blogs, Orders, StripeKeys, ArTypes, UpdateModel, CustomPage, TrackingPixel, ScanLog, TeamMember } from "../model/index.js";

export const syncAllTables = async (req, res) => {
  try {
    // Synchronize all models
    await Users.sync({ alter: true });
    await AdminSettings.sync({ alter: true });
    await Packages.sync({ alter: true });
    await blogCategories.sync({ force: true });
    await blogs.sync({ force: true });
    await Orders.sync({ alter: true });
    await StripeKeys.sync({ alter: true });
    await ArTypes.sync({ alter: true });
    await UpdateModel.sync({ alter: true });
    await CustomPage.sync({ alter: true })
    await TrackingPixel.sync({ alter: true })
    await ScanLog.sync({ alter: true })
    await TeamMember.sync({ alter: true })

    res.status(200).json({ message: "All tables synchronized successfully!" });
  } catch (err) {
    res
      .status(500)
      .json({ error: `Failed to synchronize tables: ${err.message}` });
  }
};
