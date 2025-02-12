
import express from "express";
import { adminLogin, createPackage, deletePackage, deleteUser, getAdminProfile, getAllPackages, getAllUsers, getSystemSettings, singlePackage, updateAdminProfile, updatePackage, updateSystemSettings } from "../controller/admin.controller.js";
import { isAuthenticated, isAuthorized } from "../middleware/Auth.js";
import { upload } from "../middleware/multer.js";
import { addBlog, blogCategory, deleteBlog, deleteBlogCategory, getBlogCategories, getBlogs, getSingleBlog, getSingleBlogCategory, updateBlog, updateBlogCategory } from "../controller/blogsAdmin.js";
import { stripeKeyGet, stripeKeyUpdate } from "../controller/payment.controller.js";

const adminRouter = express.Router();
// auth
adminRouter.post("/login", adminLogin);
adminRouter.get("/profile", isAuthenticated, isAuthorized("admin"), getAdminProfile);
adminRouter.post("/update-profile", isAuthenticated, isAuthorized("admin"), upload.single("profileAvatar"), updateAdminProfile);
// system settings
adminRouter.get("/system-settings", isAuthenticated, isAuthorized("admin"), getSystemSettings);
adminRouter.post("/update-system-settings", isAuthenticated, isAuthorized("admin"), upload.single("system_logo"), updateSystemSettings);
// Package
adminRouter.post("/create-package", isAuthenticated, isAuthorized("admin"), createPackage);
adminRouter.get("/packages", isAuthenticated, isAuthorized("admin"), getAllPackages);
adminRouter.post("/update-package/:packageId", isAuthenticated, isAuthorized("admin"), updatePackage);
adminRouter.delete("/delete-package/:packageId", isAuthenticated, isAuthorized("admin"), deletePackage);
adminRouter.get("/single-package/:packageId", isAuthenticated, isAuthorized("admin"), singlePackage);
// category blogs
adminRouter.post("/create-category", isAuthenticated, isAuthorized("admin"), blogCategory);
adminRouter.get("/category", isAuthenticated, isAuthorized("admin"), getBlogCategories);
adminRouter.delete("/delete-category/:category_id", isAuthenticated, isAuthorized("admin"), deleteBlogCategory);
adminRouter.put("/update-category/:category_id", isAuthenticated, isAuthorized("admin"), updateBlogCategory);
adminRouter.get("/category/:category_id", isAuthenticated, isAuthorized("admin"), getSingleBlogCategory);
// blogs
adminRouter.post("/add-blog", isAuthenticated, isAuthorized("admin"), upload.single("blog_image"), addBlog);
adminRouter.get("/blogs", isAuthenticated, isAuthorized("admin"), getBlogs);
adminRouter.delete("/delete-blog/:blog_id", isAuthenticated, isAuthorized("admin"), deleteBlog);
adminRouter.get("/single-blog/:blog_id", isAuthenticated, isAuthorized("admin"), getSingleBlog);
adminRouter.put("/update-blog/:blog_id", isAuthenticated, isAuthorized("admin"), upload.single("blog_image"), updateBlog);
// users
adminRouter.get("/users", isAuthenticated, isAuthorized("admin"), getAllUsers);
adminRouter.delete("/delete-user/:user_id", isAuthenticated, isAuthorized("admin"), deleteUser);
//  stripe
adminRouter.get("/stripe", isAuthenticated, isAuthorized("admin"), stripeKeyGet);
adminRouter.put("/stripekey-update",isAuthenticated, isAuthorized("admin"), stripeKeyUpdate);
export default adminRouter; 