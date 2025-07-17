import express from "express";
import {
  apiKeyGenerate,
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
import { allcustomPages, allTrackingPixel, AnalyzeAiImageAICode, arModelView, createARLogoModel, createARVideoModel, createCustomPage, createFaceModel, createPhotoModel, createPortalModel, createTrackingPixel, deleteTrackingPixel, generateAICodeQrCode, generateObjectModel, generateQrCodes, latestModel, qrdelete, saveScanLog, trackQrCodeScan, updatedModel, upload3Dfiles, userArModels } from "../controller/arCode.controller.js";
import { upload } from "../middleware/multer.js";
import { createPaymentAndOrder } from "../controller/payment.controller.js";
import { inviteTeamMember } from "../controller/teamWork.controller.js";
// import { checkApiKey } from "../middleware/apiKey.middelware.js";

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
// router.post("/update-model", checkApiKey, updatedModel);
router.post("/photo-model", upload.single("type_name"), createPhotoModel);
router.post("/generate-object-model", upload.single("type_name"), generateObjectModel);
router.post("/portal-model", upload.single("type_name"), createPortalModel);
router.post("/face-model", upload.single("type_name"), createFaceModel);
router.post("/video-model", upload.single("type_name"), createARVideoModel);
router.post("/logo-model", upload.single("type_name"), createARLogoModel);
router.post("/3dfile-model", upload.single("type_name"), upload3Dfiles);
router.post("/analyzed-AI-code-image", AnalyzeAiImageAICode);

router.post("/generate-qrcode", upload.single("arPhoto"), generateQrCodes);
router.post("/generate-qrcodeAICode", generateAICodeQrCode);
router.get("/get-ar-types/:id", arModelView);
router.get("/qrcode-models/:user_id", userArModels);
router.get("/get-latest-model", latestModel);
router.get("/scan-count/:modelId", trackQrCodeScan);
router.delete("/delete-qr-scan-list/:id", qrdelete);

// custom pages
router.post("/custom-page", upload.fields([
  { name: "custom_logo", maxCount: 1 },
  { name: "banner", maxCount: 1 },
]), isAuthenticated, createCustomPage);
router.get("/custom-pages-all", isAuthenticated, allcustomPages);

// tracking pixel
router.post("/tracking-pixel", isAuthenticated, createTrackingPixel);
router.get("/tracking-pixel", isAuthenticated, allTrackingPixel);
router.delete("/tracking-pixel/:pixel_id", isAuthenticated, deleteTrackingPixel);
router.post("/saveScanLog/:page_id", isAuthenticated, saveScanLog);

// stripe payment & orders
router.post("/stripe-payment", isAuthenticated, createPaymentAndOrder);

// api key Generate
router.post("/generate-apiKey", isAuthenticated, apiKeyGenerate);

// team members
router.post("/invite-team-member", isAuthenticated, inviteTeamMember);



export default router;
