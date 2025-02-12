import express from "express";
import {
  forgotPassword,
  login,
  packages,
  profileSettings,
  register,
  resendOtp,
  resetPassword,
  systemSettings,
  verifyOtp,
} from "../controller/user.controller.js";
import { isAuthenticated } from "../middleware/Auth.js";
import { blogSearch, getAllBlogs, getCategories, singleBlog } from "../controller/blogs.controller.js";
import { arTextView, generateQrCodes } from "../controller/arCode.controller.js";

const router = express.Router();
// Auth
router.post("/register", register);
router.post("/login", login);
router.post("/forgot-password", forgotPassword);
router.post("/verify-otp", verifyOtp);
router.post("/resend-otp", resendOtp);
router.post("/reset-password", resetPassword);
// profile settings
router.post("/profile-settings", isAuthenticated, profileSettings);
// system settings
router.get("/system-settings", systemSettings);
// Packages
router.get("/packages/:frequency", packages);
// blogs
router.get("/blog-categories", getCategories);
router.get("/blogs", getAllBlogs);
router.get("/blog-search/:category_id", blogSearch);
router.get("/single-blog/:blog_id", singleBlog);

// ar code generate
router.post("/generate-qrcode", generateQrCodes);
router.get("/get-ar-types/:id", arTextView);

export default router;
