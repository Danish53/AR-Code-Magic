import { asyncErrors } from "../middleware/asyncErrors.js";
import ErrorHandler from "../middleware/error.js";
import { blogCategories } from "../model/blogCategories.model.js";
import { blogs } from "../model/blogs.model.js";

// blog category
export const blogCategory = asyncErrors(async (req, res, next) => {
  const { category_name, category_slug, category_description } = req.body;

  if (!category_name || !category_description) {
    return next(new ErrorHandler("Please fill all required fields!", 400));
  }

  try {
    const category = await blogCategories.create({
      category_name,
      category_slug,
      category_description,
    });
    res.status(200).json({
      success: true,
      message: "Category created successfully!",
      category,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
});
export const getBlogCategories = asyncErrors(async (req, res, next) => {
  try {
    const category = await blogCategories.findAll();
    res.status(200).json({
      success: true,
      message: "Categories fetched successfully!",
      category,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
});
export const updateBlogCategory = asyncErrors(async (req, res, next) => {
  const { category_id } = req.params;
  const { category_name, category_slug, category_description } = req.body;
  try {
    const category = await blogCategories.findOne({
      where: { id: category_id },
    });
    if (!category) {
      return next(new ErrorHandler("Category not found!", 404));
    }
    await category.update({
      category_name,
      category_slug,
      category_description,
    });
    res.status(200).json({
      success: true,
      message: "Category updated successfully!",
      category,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
});
export const deleteBlogCategory = asyncErrors(async (req, res, next) => {
  const { category_id } = req.params;
  try {
    const category = await blogCategories.findOne({
      where: { id: category_id },
    });
    if (!category) {
      return next(new ErrorHandler("Category not found!", 404));
    }
    await category.destroy();
    res.status(200).json({
      success: true,
      message: "Category deleted successfully!",
      category,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
});
export const getSingleBlogCategory = asyncErrors(async (req, res, next) => {
  const { category_id } = req.params;
  try {
    const category = await blogCategories.findOne({
      where: { id: category_id },
    });
    if (!category) {
      return next(new ErrorHandler("Category not found!", 404));
    }
    res.status(200).json({
      success: true,
      message: "Category fetched successfully!",
      category,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
});

// Blogs
export const addBlog = asyncErrors(async (req, res, next) => {
  const { blog_category, blog_title, short_description, long_description } =
    req.body;

  if (!blog_category || !blog_title) {
    return next(new ErrorHandler("plz fill blog-category and title", 400));
  }

  try {
    if (!req.file || !req.file.path) {
      return next(new ErrorHandler("Please upload a blog image", 400));
    }
    const blog_image = req.file.path;

    const blog = await blogs.create({
      blog_category,
      blog_title,
      blog_image,
      short_description,
      long_description,
    });
    res.status(200).json({
      success: true,
      message: "Blog created successfully!",
      blog,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
});
export const getBlogs = asyncErrors(async (req, res, next) => {
  try {
    const blog = await blogs.findAll();
    res.status(200).json({
      success: true,
      message: "Blogs fetched successfully!",
      blog,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
});
export const updateBlog = asyncErrors(async (req, res, next) => {
  const { blog_id } = req.params;
  const { blog_category, blog_title, short_description, long_description } =
    req.body;
  if (!blog_category || !blog_title) {
    return next(new ErrorHandler("plz fill blog-category and title", 400));
  }
  try {
    const blog = await blogs.findOne({
      where: { id: blog_id },
    });
    if (!blog) {
      return next(new ErrorHandler("Blog not found!", 404));
    }

    const filePath = req.file?.path;

    await blog.update({
      blog_category,
      blog_title,
      blog_image: filePath || blog.blog_image,
      short_description,
      long_description,
    });
    res.status(200).json({
      success: true,
      message: "Blog updated successfully!",
      blog,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
});
export const deleteBlog = asyncErrors(async (req, res, next) => {
  const { blog_id } = req.params;
  try {
    const blog = await blogs.findOne({
      where: { id: blog_id },
    });
    if (!blog) {
      return next(new ErrorHandler("Blog not found!", 404));
    }
    await blog.destroy();
    res.status(200).json({
      success: true,
      message: "Blog deleted successfully!",
      blog,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
});
export const getSingleBlog = asyncErrors(async (req, res, next) => {
  const { blog_id } = req.params;
  try {
    const blog = await blogs.findOne({
      where: { id: blog_id },
    });
    if (!blog) {
      return next(new ErrorHandler("Blog not found!", 404));
    }
    res.status(200).json({
      success: true,
      message: "Blog fetched successfully!",
      blog,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
});
