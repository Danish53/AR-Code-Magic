import { asyncErrors } from "../middleware/asyncErrors.js";
import ErrorHandler from "../middleware/error.js";
import { blogCategories } from "../model/blogCategories.model.js";
import { blogs } from "../model/blogs.model.js";

// All blog categories
export const getCategories = asyncErrors(async (req, res, next) => {
  try {
    const categories = await blogCategories.findAll();
    res.status(200).json({
      success: true,
      message: "Categories fetched successfully!",
      categories,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
});
// all blogs
export const getAllBlogs = asyncErrors(async (req, res, next) => {
  try {
    const blog = await blogs.findAll({
      include: [
        {
          model: blogCategories,
          as: "category",
          attributes: ["id", "category_name"], // only fetch these fields
        },
      ],
    });

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
// blogs search with category
export const blogSearch = asyncErrors(async (req, res, next) => {
  const { category_id } = req.params;
  try {
    const blog = await blogs.findAll({
      where: {
        blog_category: category_id,
      },
    });

    if (!blog || blog.length === 0) {
      return next(new ErrorHandler("No blog found!", 404));
    }

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
// single blog
export const singleBlog = asyncErrors(async (req, res, next) => {
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
