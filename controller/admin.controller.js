import { asyncErrors } from "../middleware/asyncErrors.js";
import ErrorHandler from "../middleware/error.js";
import { Orders } from "../model/orders.model.js";
import { Packages } from "../model/packages.model.js";
import { AdminSettings } from "../model/settings.model.js";
import { Users } from "../model/user.model.js";
import { sendToken } from "../utils/jwtToken.js";

export const adminLogin = asyncErrors(async (req, res, next) => {
  const { email, password } = req.body;

  try {
    const user = await Users.findOne({
      where: {
        email,
        role: "admin",
      },
    });

    if (!user) {
      return res.status(401).json({
        success: false,
        message: "Email or password is invalid!",
      });
    }

    if (password !== user.password) {
      return res.status(401).json({
        success: false,
        message: "Email or password is invalid!",
      });
    }

    sendToken(user, 200, "Admin login successful!", res);
  } catch (error) {
    console.error("Error during login:", error);
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
});
export const getAdminProfile = asyncErrors(async (req, res, next) => {
  try {
    const admin = await Users.findOne({
      where: {
        role: "admin",
      },
    });

    if (!admin) {
      return res.status(404).json({
        success: false,
        message: "Admin profile not found",
      });
    }
    res.status(200).json({
      success: true,
      message: "Admin profile fetched successfully!",
      admin,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
});
export const updateAdminProfile = asyncErrors(async (req, res, next) => {
  const { user_name, email, password } = req.body;

  let admin = await Users.findOne({
    where: {
      role: "admin",
    },
  });
  if (!admin) {
    return next(new ErrorHandler("Admin not found", 404));
  }

  admin.user_name = user_name;
  admin.email = email;
  admin.password = password;

  const filePath = req.file.path;
  if (!filePath) {
    return next(new ErrorHandler("Please upload an image", 400));
  }
  admin.profileAvatar = filePath;

  await admin.save();

  res.status(200).json({
    success: true,
    message: "Profile updated successfully",
    admin,
  });
});

// all users
export const getAllUsers = asyncErrors(async (req, res, next) => {
  try {
    const users = await Users.findAll({
      where: {
        role: "user",
      },
      include: [
        {
          model: Packages,
          as: "packages",
        },
      ],
    });

    res.status(200).json({
      success: true,
      message: "Users fetched successfully!",
      data: {
        users, // Array of users
        metadata: {
          usersCount: users.length, // Total count
        },
      },
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
});
export const deleteUser = asyncErrors(async (req, res, next) => {
  const { user_id } = req.params;
  try {
    const user = await Users.findOne({ where: { id: user_id } });
    if (!user) {
      return next(new ErrorHandler("User not found!", 404));
    }
    await user.destroy();
    res.status(200).json({
      success: true,
      message: "User deleted successfully!",
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
});

// system settings
export const getSystemSettings = asyncErrors(async (req, res, next) => {
  try {
    const settings = await AdminSettings.findOne();
    if (!settings) {
      return next(new ErrorHandler("System settings not found", 404));
    }
    res.status(200).json({
      success: true,
      message: "System settings fetched successfully!",
      settings,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
});
export const updateSystemSettings = asyncErrors(async (req, res, next) => {
  const {
    system_name,
    email,
    address,
    phone,
    facebook,
    twitter,
    instagram,
    linkedin,
    youtube,
  } = req.body;

  if (system_name?.length < 3) {
    return next(
      new ErrorHandler("System name must be at least 3 characters!", 400)
    );
  }

  try {
    const settings = await AdminSettings.findOne();
    if (!settings) {
      return next(new ErrorHandler("System settings not found", 404));
    }

    settings.system_name = system_name;
    settings.email = email;
    settings.address = address;
    settings.phone = phone;
    settings.facebook = facebook;
    settings.twitter = twitter;
    settings.instagram = instagram;
    settings.linkedin = linkedin;
    settings.youtube = youtube;

    if (req.file && req.file.path) {
      settings.system_logo = req.file.path;
    }

    await settings.save();

    res.status(200).json({
      success: true,
      message: "System settings updated successfully!",
      settings,
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
});

//Packages
export const createPackage = async (req, res, next) => {
  const {
    package_name,
    package_title,
    package_price,
    discount_price,
    plan_frequency, // "monthly" or "yearly"
    description,
    scans,
    ar_codes,
    pages,
    tracking,
  } = req.body;

  if (
    !package_name ||
    !package_title ||
    package_price === undefined ||
    !plan_frequency ||
    !description ||
    scans === undefined ||
    ar_codes === undefined ||
    pages === undefined ||
    tracking === undefined
  ) {
    return next(new ErrorHandler("Please fill all required fields!", 400));
  }

  // Validate numerical fields
  if (
    isNaN(package_price) ||
    package_price < 0 ||
    (discount_price !== undefined &&
      (isNaN(discount_price) || discount_price < 0)) ||
    isNaN(scans) ||
    scans < 0 ||
    isNaN(ar_codes) ||
    ar_codes < 0 ||
    isNaN(pages) ||
    pages < 0
  ) {
    return next(new ErrorHandler("Invalid numerical values provided!", 400));
  }

  try {
    const user = await Users.findOne({ where: { role: "admin" } });
    if (!user) {
      return next(new ErrorHandler("Admin user not found!", 404));
    }

    const packageData = await Packages.create({
      package_name,
      package_title,
      package_price,
      discount_price: discount_price || 0,
      plan_frequency,
      description,
      scans,
      ar_codes,
      pages,
      tracking,
      added_by: user.id,
    });

    res.status(200).json({
      success: true,
      message: "Package created successfully!",
      packages: packageData,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
};
export const getAllPackages = async (req, res, next) => {
  try {
    const packages = await Packages.findAll();

    if (!packages) {
      return next(new ErrorHandler("Package not found!", 400));
    }

    res.status(200).json({
      success: true,
      packages,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
};
export const updatePackage = async (req, res, next) => {
  const { packageId } = req.params;
  const {
    package_name,
    package_title,
    package_price,
    discount_price,
    // discount,
    // duration,
    plan_frequency, // "monthly" or "yearly"
    description,
    scans,
    ar_codes,
    pages,
    tracking,
  } = req.body;

  try {
    const packageData = await Packages.findOne({
      where: { id: packageId },
    });

    if (!packageData) {
      return next(new ErrorHandler("Package not found!", 400));
    }

    packageData.package_name = package_name;
    packageData.package_title = package_title;
    packageData.package_price = package_price;
    packageData.discount_price = discount_price;
    // packageData.discount = discount;
    // packageData.duration = duration;
    packageData.plan_frequency = plan_frequency;
    packageData.description = description;
    packageData.scans = scans;
    packageData.ar_codes = ar_codes;
    packageData.pages = pages;
    packageData.tracking = tracking;

    await packageData.save();

    res.status(200).json({
      success: true,
      message: "Package updated successfully!",
      packages: packageData,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
};
export const deletePackage = async (req, res, next) => {
  const { packageId } = req.params;

  try {
    const packageData = await Packages.findOne({
      where: { id: packageId },
    });

    if (!packageData) {
      return next(new ErrorHandler("Package not found!", 400));
    }

    await packageData.destroy();

    res.status(200).json({
      success: true,
      message: "Package deleted successfully!",
      packages: packageData,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
};
export const singlePackage = async (req, res, next) => {
  const { packageId } = req.params;

  try {
    const packageData = await Packages.findOne({
      where: { id: packageId },
    });

    if (!packageData) {
      return next(new ErrorHandler("Package not found!", 400));
    }

    res.status(200).json({
      success: true,
      packages: packageData,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
};

//orders
export const getAllOrders = async (req, res, next) => {
  try {
    const orders = await Orders.findAll();
    res.status(200).json({
      success: true,
      orders,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
};
export const singleOrder = async (req, res, next) => {
  const { orderId } = req.params;
  try {
    const order = await Orders.findOne({
      where: { id: orderId },
    });

    if (!order) {
      return next(new ErrorHandler("Order not found!", 400));
    }

    res.status(200).json({
      success: true,
      order,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
};
export const updateOrder = async (req, res, next) => {
  const { orderId } = req.params;
  const { order_status } = req.body;
  try {
    const order = await Orders.findOne({
      where: { id: orderId },
    });

    if (!order) {
      return next(new ErrorHandler("Order not found!", 400));
    }

    order.order_status = order_status;
    await order.save();

    res.status(200).json({
      success: true,
      message: "Order updated successfully!",
      order,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
};
