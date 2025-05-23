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
import { arModelView, createARLogoModel, createARVideoModel, createFaceModel, createPhotoModel, createPortalModel, generateObjectModel, generateQrCodes, latestModel, updatedModel, userArModels } from "../controller/arCode.controller.js";
import { upload } from "../middleware/multer.js";

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
router.post("/update-model", updatedModel);
router.post("/photo-model", upload.single("type_name"), createPhotoModel);
router.post("/generate-object-model", upload.single("type_name"), generateObjectModel);
router.post("/portal-model", upload.single("type_name"), createPortalModel);
router.post("/face-model", upload.single("type_name"), createFaceModel);
router.post("/video-model", upload.single("type_name"), createARVideoModel);
router.post("/logo-model", upload.single("type_name"), createARLogoModel);

router.post("/generate-qrcode", upload.single("arPhoto"), generateQrCodes);
router.get("/get-ar-types/:id", arModelView);
router.get("/qrcode-models/:user_id", userArModels);
router.get("/get-latest-model", latestModel);

export default router;
