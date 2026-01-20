import express from "express";
import {
  apiKeyGenerate,
  forgotPassword,
  getProfile,
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
import { allcustomPages, allTrackingPixel, AnalyzeAiImageAICode, arModelView, createARLogoModel, createARVideoModel, createCustomPage, createPhotoModel, createPortalModel, createTrackingPixel, deleteCustomPage, deleteTrackingPixel, generate3DModel, generateAICodeQrCode, generateArFace, generateArLogo, generateArPhoto, generateArPlane, generateArPortal, generateArText, generateArVideo, generateObjectModel, generateQrCodes, getSingleCustomPage, latestModel, processFrameWithFace, qrdelete, saveScanLog, trackQrCodeScan, updateCustomPage, updatedModel, upload3Dfiles, uploadLogoFace, userArModels } from "../controller/arCode.controller.js";
import { upload } from "../middleware/multer.js";
import { createCheckoutSession, verifyPayment } from "../controller/payment.controller.js";
import { getTeamMembers, inviteTeamMember, removeTeamMember, updateTeamMemberPermissions } from "../controller/teamWork.controller.js";
// import { checkApiKey } from "../middleware/apiKey.middelware.js";

const router = express.Router();
// Auth
router.post("/register", register);
router.post("/login", login);
router.get("/user-profile", isAuthenticated, getProfile);
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
router.post("/update-model", isAuthenticated, updatedModel);
// router.post("/update-model", checkApiKey, updatedModel);
router.post("/photo-model", upload.single("type_name"), isAuthenticated, createPhotoModel);
router.post("/generate-object-model", upload.single("type_name"), generateObjectModel);
router.post("/portal-model", upload.single("type_name"), isAuthenticated, createPortalModel);
// router.post("/face-model", upload.single("type_name"), createFaceModel);
router.post("/video-model", upload.single("type_name"), createARVideoModel);
router.post("/logo-model", upload.single("type_name"), isAuthenticated, createARLogoModel);
router.post("/3dfile-model", upload.single("type_name"), isAuthenticated, upload3Dfiles);
router.post("/logo-ar-face", upload.single("type_name"), uploadLogoFace);
// router.post("/ar-face", processFrameWithFace);
router.post("/analyzed-AI-code-image", AnalyzeAiImageAICode);

// ar text code
router.post("/ar-text", generateArText);
router.post("/ar-photo", upload.single("arPhoto"), generateArPhoto);
router.post("/ar-portal", upload.single("arPortal"), generateArPortal);
router.post("/ar-logo", upload.single("logoFile"), generateArLogo);
router.post("/ar-3dFile", upload.single("arFile"), generate3DModel);
router.post("/generate-qrcodeAICode", generateAICodeQrCode);
router.post("/ar-video", upload.single("arVideo"), generateArVideo);
router.post("/ar-face", upload.single("arImage"), generateArFace);

router.post("/generate-qrcode", upload.single("arPhoto"), generateQrCodes);
router.get("/get-ar-types/:id", arModelView);
router.get("/qrcode-models/:user_id", userArModels);
router.get("/get-latest-model", latestModel);
router.get("/track-scan/model/:modelId", trackQrCodeScan);
router.get("/track-scan/page/:pageId", trackQrCodeScan);
router.delete("/delete-qr-scan-list/:id", qrdelete);


router.post("/plane-model", upload.single("videoFile"), generateArPlane);

// custom pages
router.post("/custom-pages", upload.fields([
  { name: "custom_logo", maxCount: 1 },
  { name: "banner", maxCount: 1 },
]), isAuthenticated, createCustomPage);
router.get("/custom-pages", isAuthenticated, allcustomPages);
router.put("/custom-pages/:id", upload.fields([
  { name: "custom_logo", maxCount: 1 },
  { name: "banner", maxCount: 1 },
]), isAuthenticated, updateCustomPage);
router.delete("/custom-pages/:id", isAuthenticated, deleteCustomPage);
router.get("/custom-pages/:id", isAuthenticated, getSingleCustomPage);

// tracking pixel
router.post("/tracking-pixels", isAuthenticated, createTrackingPixel);
router.get("/tracking-pixels", isAuthenticated, allTrackingPixel);
router.delete("/tracking-pixels/:pixel_id", isAuthenticated, deleteTrackingPixel);
router.get("/saveScanLog/:page_id", isAuthenticated, saveScanLog);

// stripe payment & orders
router.post("/stripe-payment", createCheckoutSession);
router.post("/stripe-payment-verify", verifyPayment);

// api key Generate
router.post("/generate-apiKey", isAuthenticated, apiKeyGenerate);

// team members
router.post("/invite-team-member", isAuthenticated, inviteTeamMember);
router.get("/team-members", isAuthenticated, getTeamMembers);
router.put("/team-member/:member_id/permissions", isAuthenticated, updateTeamMemberPermissions);
router.delete("/team-member/:member_id", isAuthenticated, removeTeamMember);


export default router;
