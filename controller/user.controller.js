import { Op } from "sequelize";
import { asyncErrors } from "../middleware/asyncErrors.js";
import ErrorHandler from "../middleware/error.js";
import { Users } from "../model/user.model.js";
import { sendToken } from "../utils/jwtToken.js";
import { AdminSettings } from "../model/settings.model.js";
import nodemailer from "nodemailer";
import bcrypt from "bcrypt";
import { Packages } from "../model/packages.model.js";
import crypto from "crypto";

export const generateApiKey = () => {
  return "arcoded_pk_" + crypto.randomBytes(12).toString("hex");
};
// Auth User
export const register = asyncErrors(async (req, res, next) => {
  const { user_name, email, password, confirm_password } = req.body;

  if (!user_name || !email || !password || !confirm_password) {
    return next(new ErrorHandler("Please fill full details!", 400));
  }

  if (user_name.length < 3) {
    return next(new ErrorHandler("Username must contain at least 3 characters!", 400));
  }

  if (password !== confirm_password) {
    return next(new ErrorHandler("Password do not matched!", 400));
  }

  try {
    // Check duplicate
    const [userEmail, userName] = await Promise.all([
      Users.findOne({ where: { email } }),
      Users.findOne({ where: { user_name } })
    ]);

    if (userEmail || userName) {
      return next(new ErrorHandler("User already exists!", 400));
    }

    // Find Basic Plan
    const basicPlan = await Packages.findOne({ where: { package_name: "Basic" } });

    if (!basicPlan) {
      return next(new ErrorHandler("Basic package not found", 500));
    }

    // Create user with Basic Plan
    const user = await Users.create({
      user_name,
      email,
      password,
      package_id: basicPlan.id, // must exist in Users model
      isTrial: 1,
    });

    sendToken(user, 200, "User registered successfully!", res);
  } catch (error) {
    return next(new ErrorHandler(error.message, 500));
  }
});
export const login = asyncErrors(async (req, res, next) => {
  const { emailOrUsername, password } = req.body;

  if (!emailOrUsername || !password) {
    return next(new ErrorHandler("Please fill in all fields!", 400));
  }

  const user = await Users.findOne({
    where: {
      [Op.or]: [{ email: emailOrUsername }, { user_name: emailOrUsername }],
    },
  });

  if (!user) {
    return next(new ErrorHandler("Invalid email or username!", 400));
  }

  const isPasswordMatched = await user.comparePassword(password);
  if (!isPasswordMatched) {
    return next(new ErrorHandler("Invalid user password!", 400));
  }

  sendToken(user, 200, "User logged in successfully!", res);
});
export const forgotPassword = asyncErrors(async (req, res, next) => {
  const { email } = req.body;

  try {
    const user = await Users.findOne({ where: { email } });
    if (!user) {
      return next(new ErrorHandler("Your email is not registered!", 400));
    }

    const otp = Math.floor(100000 + Math.random() * 900000).toString();
    const expiresAt = new Date(Date.now() + 1 * 60 * 1000); // OTP valid for 1 minute

    await user.update({
      otp,
      expires_at: expiresAt,
    });

    if (!process.env.USER_EMAIL || !process.env.APP_PASSWORD) {
      return next(new ErrorHandler("Email configuration is missing!", 500));
    }

    const transporter = nodemailer.createTransport({
      service: "gmail",
      auth: {
        user: process.env.USER_EMAIL,
        pass: process.env.APP_PASSWORD,
      },
      debug: true,
    });

    const mailOptions = {
      from: process.env.USER_EMAIL,
      to: user.email,
      subject: "Password Reset OTP",
      text: `Your password reset OTP is: ${user.otp}`,
    };

    // Send email
    transporter.sendMail(mailOptions, (error, info) => {
      if (error) {
        console.log("Error sending email:", error);
        return next(new ErrorHandler("Error sending email!", 400));
      } else {
        return res.status(200).json({
          success: true,
          message: "Email sent with OTP",
        });
      }
    });
  } catch (error) {
    console.error("Error processing password reset request:", error);
    return next(new ErrorHandler("Internal server error", 500));
  }
});
export const resendOtp = asyncErrors(async (req, res, next) => {
  const { email } = req.body;

  try {
    const user = await Users.findOne({ where: { email } });
    if (!user) {
      return next(new ErrorHandler("Your email is not registered!", 400));
    }

    const otp = Math.floor(100000 + Math.random() * 900000).toString();
    const expiresAt = new Date(Date.now() + 1 * 60 * 1000); // OTP valid for 1 minute

    await user.update({
      otp,
      expires_at: expiresAt,
    });

    if (!process.env.USER_EMAIL || !process.env.APP_PASSWORD) {
      return next(new ErrorHandler("Email configuration is missing!", 500));
    }

    // Create transport for sending email
    const transporter = nodemailer.createTransport({
      service: "gmail",
      auth: {
        user: process.env.USER_EMAIL,
        pass: process.env.APP_PASSWORD,
      },
      debug: true,
    });

    // Prepare email options
    const mailOptions = {
      from: process.env.USER_EMAIL,
      to: user.email,
      subject: "Password Reset OTP",
      text: `Your password reset OTP is: ${user.otp}`,
    };

    // Send email
    transporter.sendMail(mailOptions, (error, info) => {
      if (error) {
        console.log("Error sending email:", error);
        return next(new ErrorHandler("Error sending email!", 400));
      } else {
        return res.status(200).json({
          success: true,
          message: "Email sent with OTP",
        });
      }
    });
  } catch (error) {
    console.error("Error processing password reset request:", error);
    return next(new ErrorHandler("Internal server error", 500));
  }
});
export const verifyOtp = asyncErrors(async (req, res, next) => {
  const { otp } = req.body;
  try {
    const otpRecord = await Users.findOne({
      where: { otp },
    });

    if (!otpRecord) {
      return next(new ErrorHandler("Invalid or expired OTP!", 400));
    }

    if (otpRecord.expires_at < new Date()) {
      return next(new ErrorHandler("OTP has expired!", 400));
    }

    return res.status(200).json({
      success: true,
      message: "OTP verified successfully",
    });
  } catch (error) {
    console.error("Error verifying OTP:", error);
    return next(new ErrorHandler("Internal server error", 500));
  }
});
export const resetPassword = asyncErrors(async (req, res, next) => {
  const { email, password, confirm_password } = req.body;

  if (password !== confirm_password) {
    return next(new ErrorHandler("Passwords do not match!", 400));
  }

  if (!email || !password || !confirm_password) {
    return next(new ErrorHandler("Please fill full details!", 400));
  }

  try {
    const user = await Users.findOne({ where: { email } });

    if (!user) {
      console.log("User not found");
      return next(new ErrorHandler("User not found.", 400));
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    user.password = hashedPassword;
    await user.save({ hooks: false });

    const updatedUser = await Users.findOne({ where: { email } });
    if (hashedPassword === updatedUser.password) {
      console.log("Password has been correctly updated in the database.");
    } else {
      console.error("Password mismatch after saving!");
    }

    res.status(200).json({
      success: true,
      message: "Password updated successfully!",
    });
  } catch (error) {
    console.error("Error updating password:", error);
    return res.status(500).send("Internal server error");
  }
});

// Profile setings
export const profileSettings = asyncErrors(async (req, res, next) => {
  const { user_name, email, password, confirm_password } = req.body;

  if (!user_name) {
    return next(new ErrorHandler("Please enter user name!", 400));
  }
  try {
    const user = await Users.findOne({ where: { id: req.user.id } });
    if (!user) {
      return next(new ErrorHandler("User not found", 404));
    }

    if (password) {
      const hashedPassword = await bcrypt.hash(password, 10);
      user.password = hashedPassword;
      await user.save({ hooks: false });
    }


    if (password !== confirm_password) {
      return next(new ErrorHandler("Passwords do not match!", 400));
    }

    user.user_name = user_name;
    user.email = email;
    await user.save({ hooks: false });

    res.status(200).json({
      success: true,
      message: "Profile settings updated successfully!",
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
});

// system settings
export const systemSettings = asyncErrors(async (req, res, next) => {
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

//packages
export const packages = asyncErrors(async (req, res, next) => {
  const { frequency } = req.params;
  try {
    const packages = await Packages.findAll({
      where: { plan_frequency: frequency },
    });
    res.status(200).json({
      success: true,
      message: "Packages fetched successfully!",
      packages,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
});

// generate api key
export const apiKeyGenerate = asyncErrors(async (req, res, next) => {
  try {
    const userId = req.user.id;
    const newApiKey = generateApiKey();

    await Users.update({ api_key: newApiKey }, { where: { id: userId } });

    res.status(200).json({
      success: true,
      message: "API key generated successfully",
      api_key: newApiKey,
    });
  } catch (error) {
    console.error("API Key Generation Error:", error);
    res.status(500).json({
      success: false,
      message: "Failed to generate API key",
    });
  }
});
