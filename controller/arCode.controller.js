import QRCode from "qrcode";
import { v4 as uuid } from "uuid";
import { asyncErrors } from "../middleware/asyncErrors.js";
import path from "path";
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { exec, execSync } from 'child_process';
import { spawn } from 'child_process';
import ErrorHandler from "../middleware/error.js";
import { ArTypes } from "../model/arTypes.model.js";
import fs from 'fs';
import geoip from "geoip-lite";
import { UAParser } from "ua-parser-js";
import { UpdateModel } from "../model/tempUpdateModel.model.js";
import OpenAI from "openai";
import { GoogleGenerativeAI } from "@google/generative-ai";
import { CustomPage } from "../model/customPages.model.js";
import { TrackingPixel } from "../model/trackingPixel.model.js";
import { ScanLog } from "../model/scanLog.model.js";
import unzipper from "unzipper";
import axios from "axios";
import AdmZip from "adm-zip";
import cloudinary from "../config/cloudinaryConfig.js";
import { Orders } from "../model/orders.model.js";
import { Op } from "sequelize";
import ffmpeg from "fluent-ffmpeg";


const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
ffmpeg.setFfmpegPath("C:/Users/Abc/Downloads/ffmpeg-8.0-essentials_build/bin/ffmpeg.exe");
ffmpeg.setFfprobePath("C:/Users/Abc/Downloads/ffmpeg-8.0-essentials_build/bin/ffprobe.exe");

// const openai = new OpenAI({
//   apiKey: process.env.OPENAI_KEY, // Replace with your real key
// });
const genAI = new GoogleGenerativeAI(process.env.OPENAI_KEY);
const baseDir = path.join(__dirname, "..");
const uploadsDir = path.join(baseDir, "output");
const uploadsDirUpload = path.join(baseDir, "uploads");

// ar text model
export const updatedModel = async (req, res, next) => {
  const { id } = req.user;
  const user_id = id;
  const { type_name, font, color, depth, gloss, scale, orientation } = req.body;

  if (!type_name || !user_id) {
    return res.status(400).json({ error: "Required fields are missing" });
  }

  try {
    // **Find Font Path**
    const fontsDir = path.join(__dirname, "..", "fonts");
    const fontFile = fs.readdirSync(fontsDir).find(file => file.toLowerCase().includes(font.toLowerCase()));

    if (!fontFile) {
      return res.status(400).json({ error: "Font not found!" });
    }

    const fontPath = path.join(fontsDir, fontFile);

    // **Generate Model Path**
    const modelId = uuid().replace(/-/g, "").substring(0, 8);
    const baseDir = path.join(__dirname, "..");
    const uploadsDir = path.join(baseDir, "temp");

    const model_path = path.join(uploadsDir, `${user_id}_${modelId}.glb`);
    const model_usdz = path.join(uploadsDir, `${user_id}_${modelId}.usdz`);
    const scriptPath = path.join(__dirname, "scripts", "generate_model.py");

    // Run Blender Command**
    const command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${type_name}" "${fontPath}" "${color}" "${depth}" "${gloss}" "${scale}" "${orientation}" "${model_path}" "${model_usdz}"`;

    const timeout = 600000; // Timeout for the Blender process (600 seconds)

    // Wrap exec in a promise to handle timeouts
    const execPromise = new Promise((resolve, reject) => {
      const execProcess = exec(command, async (error, stdout, stderr) => {
        if (error) {
          console.error("❌ Error:", error, stderr);
          reject({ status: 500, message: "3D model generation failed" });
        } else {
          resolve(stdout);
        }
      });

      // Set timeout for the exec process
      setTimeout(() => {
        execProcess.kill();
        reject({ status: 500, message: "Blender process timed out" });
      }, timeout);
    });

    // Execute the command
    await execPromise;

    if (!fs.existsSync(model_path)) {
      return res.status(500).json({ error: "Generated model file not found" });
    }

    const modelUrl = `models/${user_id}_${modelId}.glb`;
    const modelUrlUsdz = `models/${user_id}_${modelId}.usdz`;
    const newModel = await UpdateModel.create({
      id: modelId,
      user_id,
      type_name,
      model_path: modelUrl,
      model_usdz: modelUrlUsdz
    });

    req.getIo().emit("modelUpdated", { id: modelId, model_path: modelUrl });

    res.json({
      success: true,
      message: "Model created successfully",
      data: {
        id: newModel.id,
        model_path: modelUrl,
        modelUrlUsdz
      },
    });
  } catch (error) {
    console.error("❌ Error:", error);
    res.status(error.status || 500).json({ error: error.message || "Internal server error" });
  }
};
// ar photo Model
export const createPhotoModel = async (req, res, next) => {
  const user_id = req.user.id;
  const { orientation, border, color, scale } = req.body;
  const type_name = req.file?.filename;

  if (!type_name || !user_id) {
    return res.status(400).json({ error: "Required fields are missing" });
  }

  try {
    // Find Photo Path
    const photosDir = path.join(__dirname, "..", "uploads");
    const photoPath = path.join(photosDir, type_name);

    if (!fs.existsSync(photoPath)) {
      return res.status(400).json({ error: "Photo not found!" });
    }

    // **Generate Model Path**
    const modelId = uuid().replace(/-/g, "").substring(0, 8);
    const uploadsDir = path.join(__dirname, "..", "temp");

    const modelPath = path.join(uploadsDir, `${user_id}_${modelId}.glb`);
    const scriptPath = path.join(__dirname, "scripts", "generate_photo_model.py");

    // **Blender Command**
    const command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${photoPath}" "${orientation}" "${border}" "${color}" "${scale}" "${modelPath}"`;

    console.log("Executing Blender command:", command);

    // **Run Command**
    const timeout = 600000; // 10 minutes

    const execPromise = new Promise((resolve, reject) => {
      const execProcess = exec(command, async (error, stdout, stderr) => {
        if (error) {
          console.error("❌ Blender error:", error, stderr);
          reject({ status: 500, message: "AR photo model generation failed" });
        } else {
          resolve(stdout);
        }
      });

      setTimeout(() => {
        execProcess.kill();
        reject({ status: 500, message: "Blender process timed out" });
      }, timeout);
    });

    await execPromise;

    if (!fs.existsSync(modelPath)) {
      return res.status(500).json({ error: "Generated model file not found" });
    }

    const modelUrl = `models/${user_id}_${modelId}.glb`;

    const newPhotoModel = await UpdateModel.create({
      id: modelId,
      user_id,
      type_name,
      model_path: modelUrl,
    });

    res.json({
      success: true,
      message: "Photo AR model created successfully",
      data: {
        id: newPhotoModel.id,
        model_path: modelUrl,
      },
    });

  } catch (error) {
    console.error("❌ Error:", error);
    res.status(error.status || 500).json({ error: error.message || "Internal server error" });
  }
};
// ar portal model
export const createPortalModel = async (req, res, next) => {
  const user_id = req.user.id;
  let type_name = req.file?.filename;

  if (!type_name || !user_id) {
    return res.status(400).json({ error: "Required fields are missing" });
  }

  const allowedExtensions = [".jpg", ".jpeg", ".png"];
  const fileExt = path.extname(type_name).toLowerCase();

  if (!allowedExtensions.includes(fileExt)) {
    // Delete invalid file
    const uploadedFilePath = path.join(__dirname, "..", "uploads", type_name);
    if (fs.existsSync(uploadedFilePath)) {
      fs.unlinkSync(uploadedFilePath);
    }
    return res.status(400).json({ error: "Only JPG and PNG files are allowed" });
  }

  try {
    const photosDir = path.join(__dirname, "..", "uploads");
    const photoPath = path.join(photosDir, type_name);

    if (!fs.existsSync(photoPath)) {
      return res.status(400).json({ error: "Photo 360 not found!" });
    }

    const modelId = uuid().replace(/-/g, "").substring(0, 8);
    const uploadsDir = path.join(__dirname, "..", "temp");

    if (!fs.existsSync(uploadsDir)) {
      fs.mkdirSync(uploadsDir);
    }

    const modelPath = path.join(uploadsDir, `${user_id}_${modelId}.glb`);
    const scriptPath = path.join(__dirname, "scripts", "generate_portal_model.py");

    const command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${photoPath}" "${modelPath}"`;
    console.log("Executing Blender command:", command);

    const timeout = 600000;

    const execPromise = new Promise((resolve, reject) => {
      const execProcess = exec(command, (error, stdout, stderr) => {
        if (error) {
          console.error("❌ Blender error:", error, stderr);
          reject({ status: 500, message: "AR Portal model generation failed" });
        } else {
          resolve(stdout);
        }
      });

      setTimeout(() => {
        execProcess.kill();
        reject({ status: 500, message: "Blender process timed out" });
      }, timeout);
    });

    await execPromise;

    if (!fs.existsSync(modelPath)) {
      return res.status(500).json({ error: "Generated model file not found" });
    }

    const modelUrl = `models/${user_id}_${modelId}.glb`;

    const newPhotoModel = await UpdateModel.create({
      id: modelId,
      user_id,
      type_name,
      model_path: modelUrl,
    });

    req.getIo().emit("photoModelUpdated", { id: modelId, model_path: modelUrl });

    res.json({
      success: true,
      message: "360° Photo model created successfully",
      data: {
        id: newPhotoModel.id,
        model_path: modelUrl,
      },
    });

  } catch (error) {
    console.error("❌ Error:", error);
    res.status(error.status || 500).json({ error: error.message || "Internal server error" });
  }
};
// ar logo model
export const createARLogoModel = async (req, res, next) => {
  const user_id = req.user.id;
  const { depth, gloss, scale, orientation, overlay } = req.body;
  let type_name = req.file?.filename;

  if (!type_name || !user_id) {
    return res.status(400).json({ error: "Required fields are missing" });
  }

  const allowedExtensions = [".svg"];
  const fileExt = path.extname(type_name).toLowerCase();

  if (!allowedExtensions.includes(fileExt)) {
    // Delete invalid file
    const uploadedFilePath = path.join(__dirname, "..", "uploads", type_name);
    if (fs.existsSync(uploadedFilePath)) {
      fs.unlinkSync(uploadedFilePath);
    }
    return res.status(400).json({ error: "Only .svg files are allowed" });
  }

  try {
    const photosDir = path.join(__dirname, "..", "uploads");
    const logoPath = path.join(photosDir, type_name);

    if (!fs.existsSync(logoPath)) {
      return res.status(400).json({ error: "logo not found!" });
    }

    const modelId = uuid().replace(/-/g, "").substring(0, 8);
    const uploadsDir = path.join(__dirname, "..", "temp");

    if (!fs.existsSync(uploadsDir)) {
      fs.mkdirSync(uploadsDir);
    }

    const modelPath = path.join(uploadsDir, `${user_id}_${modelId}.glb`);
    const model_usdz = path.join(uploadsDir, `${user_id}_${modelId}.usdz`);
    const scriptPath = path.join(__dirname, "scripts", "generate_logo_model.py");

    const command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${logoPath}" "${depth}" "${gloss}" "${scale}" "${orientation}" "${overlay}" "${modelPath}" "${model_usdz}"`;
    console.log("Executing Blender command:", command);

    const timeout = 600000;

    const execPromise = new Promise((resolve, reject) => {
      const execProcess = exec(command, (error, stdout, stderr) => {
        if (error) {
          console.error("❌ Blender error:", error, stderr, stdout);
          reject({ status: 500, message: "AR logo model generation failed" });
        } else {
          resolve(stdout);
        }
      });

      setTimeout(() => {
        execProcess.kill();
        reject({ status: 500, message: "Blender process timed out" });
      }, timeout);
    });

    await execPromise;

    if (!fs.existsSync(modelPath)) {
      return res.status(500).json({ error: "Generated model file not found glb" });
    }

    if (!fs.existsSync(model_usdz)) {
      return res.status(500).json({ error: "Generated model file not found usdz" });
    }

    const modelUrl = `models/${user_id}_${modelId}.glb`;

    const newPhotoModel = await UpdateModel.create({
      id: modelId,
      user_id,
      type_name,
      model_path: modelUrl,
    });

    // req.getIo().emit("photoModelUpdated", { id: modelId, model_path: modelUrl });

    res.json({
      success: true,
      message: "Ar Logo model created successfully",
      data: {
        id: newPhotoModel.id,
        model_path: modelUrl,
        type_name
      },
    });

  } catch (error) {
    console.error("❌ Error:", error);
    res.status(error.status || 500).json({ error: error.message || "Internal server error" });
  }
};
// ar 3d files
export const upload3Dfiles = async (req, res, next) => {
  const user_id = req.user.id;
  let type_name = req.file?.filename;

  if (!type_name || !user_id) {
    return res.status(400).json({ error: "Required fields are missing" });
  }

  // Allowed 3D file extensions (lowercase)
  const allowedExtensions = [
    ".glb", ".usdz", ".ply", ".stl", ".fbx", ".obj", ".x3d", ".gltf", ".zip"
  ];
  const fileExt = path.extname(type_name).toLowerCase();

  if (!allowedExtensions.includes(fileExt)) {
    // Delete invalid file
    const uploadedFilePath = path.join(__dirname, "..", "uploads", type_name);
    if (fs.existsSync(uploadedFilePath)) {
      fs.unlinkSync(uploadedFilePath);
    }
    return res.status(400).json({
      error: `Invalid file type. Only these 3D formats are allowed: ${allowedExtensions.join(", ")}`
    });
  }

  try {
    const uploadsDir = path.join(__dirname, "..", "uploads");
    const modelInputPath = path.join(uploadsDir, type_name);

    if (!fs.existsSync(modelInputPath)) {
      return res.status(400).json({ error: "Uploaded model file not found!" });
    }

    // Check file size (e.g., 100MB limit)
    const stats = fs.statSync(modelInputPath);
    const fileSizeInMB = stats.size / (1024 * 1024);
    if (fileSizeInMB > 100) {
      fs.unlinkSync(modelInputPath);
      return res.status(400).json({ error: "File size exceeds 100MB limit" });
    }

    const modelId = uuid().replace(/-/g, "").substring(0, 8);
    const tempDir = path.join(__dirname, "..", "temp");

    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true });
    }

    // Output paths
    const outputGLB = path.join(tempDir, `${user_id}_${modelId}.glb`);
    const outputUSDZ = path.join(tempDir, `${user_id}_${modelId}.usdz`);

    // Python script to run Blender conversion
    const scriptPath = path.join(__dirname, "scripts", "convert_3d_files.py");

    // Blender command
    const command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${modelInputPath}" "${outputGLB}" "${outputUSDZ}"`;
    console.log("Executing Blender command:", command);

    const timeout = 600000; // 10 minutes

    const execPromise = new Promise((resolve, reject) => {
      const execProcess = exec(command, (error, stdout, stderr) => {
        if (error) {
          console.error("❌ Blender error:", error, stderr, stdout);
          reject({ status: 500, message: "3D model conversion failed: " + (stderr || stdout || error.message) });
        } else {
          resolve(stdout);
        }
      });

      setTimeout(() => {
        execProcess.kill();
        reject({ status: 500, message: "Blender process timed out after 10 minutes" });
      }, timeout);
    });

    await execPromise;

    // Verify outputs were created
    const glbExists = fs.existsSync(outputGLB);
    const usdzExists = fs.existsSync(outputUSDZ);

    if (!glbExists && !usdzExists) {
      return res.status(500).json({ error: "Conversion failed - no output files were created" });
    }

    // Clean up the original uploaded file
    fs.unlinkSync(modelInputPath);

    const modelUrl = `models/${user_id}_${modelId}.glb`;

    const newModel = await UpdateModel.create({
      id: modelId,
      user_id,
      type_name,
      model_path: modelUrl,
    });

    res.json({
      success: true,
      message: "3D model created and converted successfully",
      data: {
        id: newModel.id,
        model_path: modelUrl,
        type_name,
        formats: {
          glb: glbExists,
          usdz: usdzExists
        }
      },
    });

  } catch (error) {
    console.error("❌ Error:", error);

    // Clean up any temporary files that might have been created
    try {
      if (outputGLB && fs.existsSync(outputGLB)) fs.unlinkSync(outputGLB);
      if (outputUSDZ && fs.existsSync(outputUSDZ)) fs.unlinkSync(outputUSDZ);
    } catch (cleanupError) {
      console.error("Cleanup error:", cleanupError);
    }

    res.status(error.status || 500).json({
      error: error.message || "Internal server error during 3D model processing"
    });
  }
};

// ar face model
// export const createFaceModel = async (req, res, next) => {
//   const { user_id } = req.body;
//   const type_name = req.file?.filename;

//   if (!type_name || !user_id) {
//     return res.status(400).json({ error: "Required fields are missing" });
//   }

//   const allowedExtensions = [".jpg", ".jpeg", ".png"];
//   const fileExt = path.extname(type_name).toLowerCase();

//   if (!allowedExtensions.includes(fileExt)) {
//     const filePath = path.join(__dirname, "..", "uploads", type_name);
//     if (fs.existsSync(filePath)) fs.unlinkSync(filePath);
//     return res.status(400).json({ error: "Only JPG and PNG files are allowed" });
//   }

//   let modelPath;

//   try {
//     const photoPath = path.join(__dirname, "..", "uploads", type_name);
//     const modelId = uuid().replace(/-/g, "").substring(0, 8);

//     // Create temp directory if it doesn't exist
//     const tempDir = path.join(__dirname, "..", "temp");
//     if (!fs.existsSync(tempDir)) {
//       fs.mkdirSync(tempDir, { recursive: true });
//     }

//     modelPath = path.join(tempDir, `${user_id}_${modelId}.glb`);
//     const scriptPath = path.join(__dirname, "scripts", "generate_face_filter_model.py");

//     // Verify Blender path exists
//     if (!process.env.BLENDER_PATH || !fs.existsSync(process.env.BLENDER_PATH)) {
//       throw new Error("Blender executable not found at configured path");
//     }

//     // Verify script exists
//     if (!fs.existsSync(scriptPath)) {
//       throw new Error(`Python script not found at ${scriptPath}`);
//     }

//     const command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${photoPath}" "${modelPath}"`;
//     console.log("🔧 Running Blender Command:", command);

//     const timeout = 600000; // 10 minutes
//     const { stdout, stderr } = await new Promise((resolve, reject) => {
//       const execProcess = exec(command, (error, stdout, stderr) => {
//         if (error) {
//           reject({
//             error: error,
//             stdout: stdout,
//             stderr: stderr
//           });
//         } else {
//           resolve({ stdout, stderr });
//         }
//       });

//       setTimeout(() => {
//         execProcess.kill();
//         reject(new Error("Blender process timed out after 10 minutes"));
//       }, timeout);
//     });

//     console.log("Blender stdout:", stdout);
//     console.error("Blender stderr:", stderr);

//     // Additional check - wait briefly if file is being written
//     let attempts = 0;
//     while (!fs.existsSync(modelPath) && attempts < 5) {
//       await new Promise(resolve => setTimeout(resolve, 500));
//       attempts++;
//     }

//     if (!fs.existsSync(modelPath)) {
//       console.error("Expected output file not found:", modelPath);
//       console.error("Directory contents:", fs.readdirSync(tempDir));
//       throw new Error("Generated face model file not found after Blender execution");
//     }

//     // Verify the GLB file has content
//     const stats = fs.statSync(modelPath);
//     if (stats.size === 0) {
//       fs.unlinkSync(modelPath);
//       throw new Error("Generated GLB file is empty (0 bytes)");
//     }

//     if (!fs.existsSync(modelPath)) {
//       return res.status(500).json({ error: "Generated model file not found" });
//     }

//     const modelUrl = `models/${user_id}_${modelId}.glb`;

//     const newFaceModel = await UpdateModel.create({
//       id: modelId,
//       user_id,
//       type_name,
//       model_path: modelUrl,
//     });

//     // req.getIo().emit("photoModelUpdated", { id: modelId, model_path: modelUrl });

//     res.json({
//       success: true,
//       message: "face model created successfully",
//       data: {
//         id: newFaceModel.id,
//         model_path: modelUrl,
//       },
//     });

//   } catch (error) {
//     console.error("❌ Full Error Details:", {
//       message: error.message,
//       stdout: error.stdout,
//       stderr: error.stderr,
//       stack: error.stack
//     });

//     // Clean up any partial files
//     if (modelPath && fs.existsSync(modelPath)) {
//       try {
//         fs.unlinkSync(modelPath);
//       } catch (cleanupError) {
//         console.error("Failed to clean up temp file:", cleanupError);
//       }
//     }

//     res.status(500).json({
//       error: "AR model generation failed",
//       details: process.env.NODE_ENV === 'development' ? error.message : undefined
//     });
//   }
// };
export const uploadLogoFace = async (req, res, next) => {
  const { user_id } = req.body;
  const type_name = req.file?.filename;

  if (!type_name || !user_id) {
    return res.status(400).json({ error: "Required fields are missing" });
  }

  const allowedExtensions = [".jpg", ".jpeg", ".png"];
  const fileExt = path.extname(type_name).toLowerCase();

  if (!allowedExtensions.includes(fileExt)) {
    const filePath = path.join(__dirname, "..", "uploads", type_name);
    if (fs.existsSync(filePath)) fs.unlinkSync(filePath);
    return res.status(400).json({ error: "Only JPG and PNG files are allowed" });
  }

  try {
    const logoId = uuid().replace(/-/g, "").substring(0, 8);
    const filePath = path.join(__dirname, "..", "uploads", type_name);

    // DB me save
    const newLogo = await UpdateModel.create({
      id: logoId,
      user_id,
      type_name: filePath,
    });

    // QR code generate with link
    const routeUrl = `${process.env.FRONTEND}ar-text/${logoId}`;
    const qrImage = await QRCode.toDataURL(routeUrl);

    res.json({
      success: true,
      message: "Logo uploaded & QR generated",
      data: {
        newLogo,
        logoId,
        qrImage,
        routeUrl,
      },
    });
  } catch (error) {
    console.error("❌ Upload/QR error:", error);
    res.status(500).json({ error: "Logo upload or QR generation failed" });
  }
};

export const processFrameWithFace = async (req, res, next) => {
  try {
    const { frame, logoId } = req.body;
    if (!frame || !logoId) {
      return res.status(400).json({ error: "Frame aur logoId required hain" });
    }

    // DB se logo fetch
    const logo = await UpdateModel.findOne({ where: { id: logoId } });
    if (!logo) {
      return res.status(404).json({ error: "Logo not found" });
    }

    // Logo ko base64 me convert karo
    const logoBuffer = fs.readFileSync(logo.type_name);
    console.log(logo.type_name, "logo ")
    const logoBase64 = "data:image/png;base64," + logoBuffer.toString("base64");
    // console.log(logoBase64, "logo base 64")

    const scriptPath = path.join(__dirname, "scripts", "generate_face_filter_model.py");
    // Python script run karo
    const py = spawn("python", [scriptPath]);

    let dataString = "";
    py.stdout.on("data", (data) => {
      dataString += data.toString();
    });

    py.stderr.on("data", (err) => {
      console.error("Python error:", err.toString());
    });

    py.on("close", () => {
      try {
        const output = JSON.parse(dataString);
        return res.json(output); // processed frame return
      } catch (err) {
        return res.status(500).json({ error: "Python invalid response" });
      }
    });

    py.stdin.write(JSON.stringify({ frame, logo: logoBase64 }));
    py.stdin.end();

  } catch (error) {
    console.error("❌ Frame process error:", error);
    res.status(500).json({ error: "Frame processing failed" });
  }
};
// ar video model
export const createARVideoModel = async (req, res, next) => {
  const { user_id } = req.body;
  let type_name = req.file?.filename;

  if (!type_name || !user_id) {
    return res.status(400).json({ error: "Required fields are missing" });
  }

  const allowedExtensions = [".mp4", ".mov"];
  const fileExt = path.extname(type_name).toLowerCase();

  if (!allowedExtensions.includes(fileExt)) {
    // Delete invalid file
    const uploadedFilePath = path.join(__dirname, "..", "uploads", type_name);
    if (fs.existsSync(uploadedFilePath)) {
      fs.unlinkSync(uploadedFilePath);
    }
    return res.status(400).json({ error: "Only .mp4 and .mov files are allowed" });
  }

  try {
    const photosDir = path.join(__dirname, "..", "uploads");
    const videoPath = path.join(photosDir, type_name);

    if (!fs.existsSync(videoPath)) {
      return res.status(400).json({ error: "video not found!" });
    }

    const modelId = uuid().replace(/-/g, "").substring(0, 8);
    const uploadsDir = path.join(__dirname, "..", "temp");

    if (!fs.existsSync(uploadsDir)) {
      fs.mkdirSync(uploadsDir);
    }

    const modelPath = path.join(uploadsDir, `${user_id}_${modelId}.glb`);
    const scriptPath = path.join(__dirname, "scripts", "generate_video_model.py");

    const defaultImage = path.join(__dirname, "..", "uploads", "my-pic.jpg");
    if (!fs.existsSync(defaultImage)) {
      throw new Error("Default image not found at " + defaultImage);
    }


    const command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${modelPath}" "${videoPath}" "${defaultImage}"`;
    console.log("Executing Blender command:", command);

    const timeout = 600000;

    const execPromise = new Promise((resolve, reject) => {
      const execProcess = exec(command, (error, stdout, stderr) => {
        if (error) {
          console.error("❌ Blender error:", error, stderr);
          reject({ status: 500, message: "AR video model generation failed" });
        } else {
          resolve(stdout);
        }
      });

      setTimeout(() => {
        execProcess.kill();
        reject({ status: 500, message: "Blender process timed out" });
      }, timeout);
    });

    await execPromise;

    if (!fs.existsSync(modelPath)) {
      return res.status(500).json({ error: "Generated model file not found" });
    }

    const modelUrl = `models/${user_id}_${modelId}.glb`;

    const newPhotoModel = await UpdateModel.create({
      id: modelId,
      user_id,
      type_name,
      model_path: modelUrl,
    });

    req.getIo().emit("photoModelUpdated", { id: modelId, model_path: modelUrl });

    res.json({
      success: true,
      message: "Ar video model created successfully",
      data: {
        id: newPhotoModel.id,
        model_path: modelUrl,
        type_name
      },
    });

  } catch (error) {
    console.error("❌ Error:", error);
    res.status(error.status || 500).json({ error: error.message || "Internal server error" });
  }
};


// ar object model 
// export const generateObjectModel = async (req, res) => {
//   const { user_id } = req.body;
//   const videoFile = req.file;

//   if (!videoFile || !user_id) {
//     return res.status(400).json({ error: "Missing required fields" });
//   }

//   try {
//     const modelId = uuid().replace(/-/g, '').substring(0, 8);
//     const outputDir = path.join(__dirname, '../temp');
//     const outputPath = path.join(outputDir, `${user_id}_${modelId}.glb`);
//     const outputPathUsdz = path.join(outputDir, `${user_id}_${modelId}.usdz`);
//     // const videoPath = path.join(videoFile.destination, videoFile.filename);
//     const videoPath = path.join(uploadsDirUpload, videoFile.filename);

//     if (!fs.existsSync(outputDir)) {
//       fs.mkdirSync(outputDir, { recursive: true });
//     }

//     const scriptPath = path.join(__dirname, './scripts/generate_object_model.py');
//     const command = `python "${scriptPath}" "${videoPath}" "${outputPath}"`;

//     console.log("Running command:", command);

//     exec(command, { maxBuffer: 1024 * 1024 * 50 }, async (error, stdout, stderr) => {
//       console.log("STDOUT:", stdout);
//       if (stderr) console.error("STDERR:", stderr);

//       if (error) {
//         console.error("Exec error:", error);
//         return res.status(500).json({ error: "Model generation failed", details: error.message });
//       }

//       if (!fs.existsSync(outputPath)) {
//         return res.status(500).json({
//           error: "Model generation failed",
//           details: stderr || stdout || "Unknown error"
//         });
//       }

//       try {

//         if (!fs.existsSync(outputPath)) {
//           console.error("Output GLB file does not exist:", outputPath);
//           return res.status(500).json({
//             error: "Model generation failed",
//             details: stderr || stdout || "Unknown error"
//           });
//         }

//         // Ensure public/models directory exists
//         const publicDir = path.join(__dirname, '../../public/models');
//         if (!fs.existsSync(publicDir)) {
//           fs.mkdirSync(publicDir, { recursive: true });
//         }

//         // Move the file from temp to public/models
//         const finalPath = path.join(outputDir, `${user_id}_${modelId}.glb`);
//         await fs.promises.rename(outputPath, finalPath);
//         // console.log(`Moved GLB file to ${finalPath}`);

//         // Delete the uploaded video (optional)
//         if (fs.existsSync(videoPath)) {
//           await fs.promises.unlink(videoPath);
//         }

//         // Save model info to DB **after** file is successfully moved
//         const modelUrl = `models/${user_id}_${modelId}.glb`;
//         await UpdateModel.create({
//           id: modelId,
//           user_id,
//           model_path: modelUrl,
//           type_name: videoFile.originalname,
//         });

//         return res.status(200).json({
//           success: true,
//           data: {
//             id: modelId,
//             model_path: modelUrl,
//           },
//         });
//       } catch (dbError) {
//         console.error("Database error:", dbError);
//         if (fs.existsSync(outputPath)) {
//           await fs.promises.unlink(outputPath);
//         }
//         return res.status(500).json({ error: "Failed to save model" });
//       }
//     });
//   } catch (err) {
//     console.error("Unexpected error:", err);
//     return res.status(500).json({ error: "Internal server error" });
//   }
// };
const MESHY_API_KEY = process.env.MESHY_API_KEY;
if (!MESHY_API_KEY) {
  console.error("MESHY_API_KEY not defined in .env");
}

// export const generateObjectModel = asyncErrors(async (req, res, next) => {
//   const user_id = req.body.user_id;
//   const zipFile = req.file;

//   if (!user_id || !zipFile) {
//     return res.status(400).json({ error: "Missing user_id or zip file" });
//   }

//   console.log("ZIP received:", zipFile.filename);

//   try {
//     const modelId = uuid().replace(/-/g, "").slice(0, 8);
//     const tempExtractPath = path.join("uploads", `extract_${modelId}`);

//     // ✅ Step 1: Extract ZIP
//     const zip = new AdmZip(zipFile.path);
//     zip.extractAllTo(tempExtractPath, true);
//     console.log("ZIP extracted to:", tempExtractPath);

//     // ✅ Step 2: Handle nested folder
//     let searchPath = tempExtractPath;
//     const extractedItems = fs.readdirSync(tempExtractPath);
//     if (
//       extractedItems.length === 1 &&
//       fs.lstatSync(path.join(tempExtractPath, extractedItems[0])).isDirectory()
//     ) {
//       searchPath = path.join(tempExtractPath, extractedItems[0]);
//       console.log("Found inner folder:", searchPath);
//     }

//     // ✅ Step 3: Get all image files
//     const allFiles = fs.readdirSync(searchPath);
//     const imageFiles = allFiles.filter(f => /\.(jpg|jpeg|png)$/i.test(f));

//     if (imageFiles.length === 0) {
//       return res.status(400).json({ error: "No images found in ZIP file" });
//     }

//     // ✅ Step 4: Upload each image to Cloudinary
//     const imageUrls = [];
//     for (const file of imageFiles) {
//       const filePath = path.join(searchPath, file);
//       const uploadResult = await cloudinary.uploader.upload(filePath, {
//         folder: "meshy_uploads",
//       });
//       imageUrls.push(uploadResult.secure_url);
//       console.log("Uploaded to Cloudinary:", uploadResult.secure_url);
//     }

//     // ✅ Step 5: Send Cloudinary URLs to Meshy API
//     const createResp = await axios.post(
//       "https://api.meshy.ai/openapi/v1/multi-image-to-3d",
//       {
//         image_urls: imageUrls,
//         should_remesh: true,
//         should_texture: true,
//         enable_pbr: true,
//         ai_model: "meshy-5",
//       },
//       {
//         headers: {
//           Authorization: `Bearer ${MESHY_API_KEY}`,
//           "Content-Type": "application/json",
//         },
//         timeout: 10 * 60 * 1000,
//       }
//     );

//     const taskId = createResp.data.result;
//     console.log("Meshy task created:", taskId);

//     // ✅ Step 6: Poll for result
//     let model_urls = null;
//     while (true) {
//       const statusResp = await axios.get(
//         `https://api.meshy.ai/openapi/v1/multi-image-to-3d/${taskId}`,
//         { headers: { Authorization: `Bearer ${MESHY_API_KEY}` } }
//       );

//       const statusData = statusResp.data;

//       if (statusData.status === "SUCCEEDED") {
//         model_urls = statusData.model_urls;
//         break;
//       }
//       if (statusData.status === "FAILED") {
//         return res
//           .status(500)
//           .json({ error: "Meshy model generation failed", details: statusData });
//       }

//       console.log("Waiting for Meshy process…", statusData.status, statusData.progress);
//       await new Promise(r => setTimeout(r, 5000));
//     }

//     // ✅ Step 7: Clean up local files
//     fs.unlinkSync(zipFile.path);
//     fs.rmSync(tempExtractPath, { recursive: true, force: true });

//     // ✅ Step 8: Save to DB
//     await ArTypes.create({
//       id: modelId,
//       user_id,
//       model_path: model_urls.glb,
//       model_usdz: model_urls.usdz,
//     });

//     // ✅ Step 9: Return model URLs
//     res.status(200).json({
//       success: true,
//       data: {
//         id: modelId,
//         glb_url: model_urls.glb,
//         usdz_url: model_urls.usdz,
//       },
//     });
//   } catch (err) {
//     console.error("Generate 3D error:", err);
//     return res
//       .status(500)
//       .json({ error: "Internal server error", details: err.toString() });
//   }
// });

// export const generateObjectModel = asyncErrors(async (req, res, next) => {
//   const user_id = req.body.user_id;
//   const zipFile = req.file; // aap chaho to single image bhi req.file se pass kar sakte ho

//   if (!user_id || !zipFile) {
//     return res.status(400).json({ error: "Missing user_id or image file" });
//   }

//   console.log("Image received:", zipFile.filename);

//   try {
//     const modelId = uuid().replace(/-/g, "").slice(0, 8);

//     // ✅ Step 1: Upload to Cloudinary (real upload, ya skip karke mock URL use kar sakte ho)
//     const imageUrls = [
//       `https://res.cloudinary.com/demo/image/upload/v000000/${zipFile.filename}`
//     ];
//     console.log("Mock Uploaded URL:", imageUrls[0]);

//     // ✅ Step 2: Fake Meshy API response for local testing
//     const taskId = "fake_task_id_" + modelId;
//     console.log("Fake Meshy task created:", taskId);

//     // ✅ Step 3: Fake polling loop
//     let model_urls = {
//       glb: "https://example.com/fake_model.glb",
//       usdz: "https://example.com/fake_model.usdz"
//     };

//     // ✅ Step 4: Clean up local files
//     fs.unlinkSync(zipFile.path);

//     // ✅ Step 5: Save to DB (optional, can skip if you want local testing only)
//     await UpdateModel.create({
//       id: modelId,
//       user_id,
//       type_name: "mock_model",
//       model_path: model_urls.glb,
//       model_usdz: model_urls.usdz,
//     });

//     // ✅ Step 6: Return fake model URLs
//     res.status(200).json({
//       success: true,
//       data: {
//         id: modelId,
//         glb_url: model_urls.glb,
//         usdz_url: model_urls.usdz,
//       },
//     });
//   } catch (err) {
//     console.error("Generate 3D error (mock mode):", err);
//     return res
//       .status(500)
//       .json({ error: "Internal server error", details: err.toString() });
//   }
// });


// export const generateObjectModel = asyncErrors(async (req, res, next) => {
//   const user_id = req.body.user_id;
//   const zipFile = req.file; // single image upload

//   if (!user_id || !zipFile) {
//     return res.status(400).json({ error: "Missing user_id or image file" });
//   }

//   console.log("Image received:", zipFile.filename);

//   try {
//     const modelId = uuid().replace(/-/g, "").slice(0, 8);

//     // --- Step 1: Save fake GLB/USDZ files locally ---
//     const glbFilename = `model_${modelId}.glb`;
//     const usdzFilename = `model_${modelId}.usdz`;

//     const glbPath = path.join(uploadsDir, glbFilename);
//     const usdzPath = path.join(uploadsDir, usdzFilename);

//     // For testing, you can copy some dummy GLB/USDZ files into these paths
//     // Or just create empty files for now
//     fs.writeFileSync(glbPath, ""); 
//     fs.writeFileSync(usdzPath, "");

//     console.log("Mock GLB/USDZ saved:", glbPath, usdzPath);

//     // --- Step 2: Clean up uploaded image ---
//     fs.unlinkSync(zipFile.path);

//     // --- Step 3: Save info to DB ---
//     await UpdateModel.create({
//       id: modelId,
//       user_id,
//       type_name: "mock_model",
//       model_path: `/uploads/mock_models/${glbFilename}`,
//       model_usdz: `/uploads/mock_models/${usdzFilename}`,
//     });

//     // --- Step 4: Return URLs pointing to backend ---
//     res.status(200).json({
//       success: true,
//       data: {
//         id: modelId,
//         glb_url: `/uploads/mock_models/${glbFilename}`,
//         usdz_url: `/uploads/mock_models/${usdzFilename}`,
//       },
//     });
//   } catch (err) {
//     console.error("Generate 3D error (mock mode):", err);
//     return res
//       .status(500)
//       .json({ error: "Internal server error", details: err.toString() });
//   }
// });

export const generateObjectModel = asyncErrors(async (req, res, next) => {
  const user_id = req.body.user_id;
  const imageFile = req.file;

  if (!user_id || !imageFile) {
    return res.status(400).json({ error: "Missing user_id or image file" });
  }

  console.log("Image received:", imageFile.filename);

  try {
    const modelId = uuid().replace(/-/g, "").slice(0, 8);

    // ✅ Step 1: Upload image to Cloudinary
    const uploadResult = await cloudinary.uploader.upload(imageFile.path, {
      folder: "meshy_single_uploads",
    });
    const imageUrl = uploadResult.secure_url;
    console.log("Uploaded to Cloudinary:", imageUrl);

    // ✅ Step 2: Send request to Meshy Image-to-3D API
    const createResp = await axios.post(
      "https://api.meshy.ai/openapi/v1/image-to-3d",
      {
        image_url: imageUrl,
        enable_pbr: false, // keep lightweight for free plan
        should_texture: true,
      },
      {
        headers: {
          Authorization: `Bearer ${MESHY_API_KEY}`,
          "Content-Type": "application/json",
        },
      }
    );

    const taskId = createResp.data.result;
    console.log("Meshy task created:", taskId);

    // ✅ Step 3: Poll for result
    let model_urls = null;
    while (true) {
      const statusResp = await axios.get(
        `https://api.meshy.ai/openapi/v1/image-to-3d/${taskId}`,
        { headers: { Authorization: `Bearer ${MESHY_API_KEY}` } }
      );

      const statusData = statusResp.data;

      if (statusData.status === "SUCCEEDED") {
        model_urls = statusData.model_urls;
        break;
      }
      if (statusData.status === "FAILED") {
        return res
          .status(500)
          .json({ error: "Meshy model generation failed", details: statusData });
      }

      console.log(
        "Waiting for Meshy process…",
        statusData.status,
        statusData.progress
      );
      await new Promise((r) => setTimeout(r, 5000));
    }

    // ✅ Step 4: Clean up local files
    fs.unlinkSync(imageFile.path);

    // ✅ Step 5: Save to DB (optional)
    await ArTypes.create({
      id: modelId,
      user_id,
      model_path: model_urls.glb,
      model_usdz: model_urls.usdz,
    });

    // ✅ Step 6: Return model URLs
    res.status(200).json({
      success: true,
      data: {
        id: modelId,
        glb_url: model_urls.glb,
        usdz_url: model_urls.usdz,
      },
    });
  } catch (err) {
    console.error("Generate 3D error:", err);
    return res
      .status(500)
      .json({ error: "Internal server error", details: err.toString() });
  }
});

export const latestModel = asyncErrors(async (req, res, next) => {
  const glbPath = path.join(uploadsDir, "updated_model.glb");

  if (fs.existsSync(glbPath)) {
    res.json({ success: true, modelUrl: `http://localhost:${PORT}/models/147e4f26.glb?${Date.now()}` });
  } else {
    res.status(404).json({ success: false, message: "Model not found" });
  }
});

// Ar Text model create
export const generateArText = asyncErrors(async (req, res, next) => {
  const {
    ar_type,
    type_name,
    font,
    color,
    depth,
    gloss,
    scale,
    orientation,
    reference_name,
    content,
    user_id,
    url,
    password,
    tracking_pixel,
    custom_page,
    border,
    overlay
  } = req.body;

  if (!ar_type || !type_name || !font || !color || !depth || !gloss || !scale || !orientation || !user_id) {
    return next(new ErrorHandler("Missing required fields for AR Text", 400));
  }

  const baseDir = path.join(__dirname, "..");
  // const uploadsDir = path.join(baseDir, "uploads");
  if (!fs.existsSync(uploadsDir)) fs.mkdirSync(uploadsDir, { recursive: true });

  await UpdateModel.destroy({ where: { user_id } });

  const modelId = uuid().replace(/-/g, "").substring(0, 8);
  const modelPath = path.join(uploadsDir, `${user_id}_${modelId}.glb`);
  const modelPathusdz = path.join(uploadsDir, `${user_id}_${modelId}.usdz`);

  const scriptPath = path.join(__dirname, "scripts", "generate_model.py");

  console.log("🧠 Using Blender path:", process.env.BLENDER_PATH);

  const command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${type_name}" "${font}" "${color}" "${depth}" "${gloss}" "${scale}" "${orientation}" "${modelPath}" "${modelPathusdz}"`;
  console.log("🔧 Executing Blender command:", command);

  await new Promise((resolve, reject) => {
    const process = exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error("❌ Blender Error:", stderr || stdout);
        return reject(new ErrorHandler("Blender model generation failed", 500));
      }
      console.log("✅ Blender output:", stdout);
      resolve(stdout);
    });

    setTimeout(() => {
      process.kill();
      reject(new ErrorHandler("Blender process timeout", 500));
    }, 600000);
  });

  if (!fs.existsSync(modelPath) || !fs.existsSync(modelPathusdz)) {
    return next(new ErrorHandler("Generated model not found", 500));
  }

  const qrCodeUrl = custom_page
    ? `${process.env.FRONTEND_URL}user/page/${custom_page}`
    : `${process.env.FRONTEND_URL}ar-text/${modelId}`;
  const qrCodeImage = await QRCode.toDataURL(qrCodeUrl);

  const newAR = await ArTypes.create({
    id: modelId,
    type_name,
    ar_type,
    font,
    color,
    depth,
    gloss,
    scale,
    orientation,
    reference_name,
    content,
    url,
    password,
    tracking_pixel,
    custom_page,
    user_id,
    border,
    qr_code: qrCodeImage,
    model_path: `models/${user_id}_${modelId}.glb`,
    model_usdz: `models/${user_id}_${modelId}.usdz`,
    overlay
  });

  res.json({
    success: true,
    message: "AR Text QR Code created",
    data: newAR,
  });
});
// Ar Photo model create
export const generateArPhoto = asyncErrors(async (req, res, next) => {
  const {
    ar_type,
    user_id,
    orientation,
    border,
    color,
    scale,
    custom_page,
    tracking_pixel,
    reference_name,
    content,
    url,
    password,
  } = req.body;

  const arPhoto = req.file;

  if (!user_id || !arPhoto) {
    return next(new ErrorHandler("User ID and photo are required", 400));
  }

  // Base directories
  const baseDir = path.join(__dirname, "..");
  const uploadsDirec = path.join(baseDir, "uploads");
  if (!fs.existsSync(uploadsDir)) fs.mkdirSync(uploadsDir);

  // Clean up old models for this user
  await UpdateModel.destroy({ where: { user_id } });

  const modelId = uuid().replace(/-/g, "").substring(0, 8);
  const modelPath = path.join(uploadsDir, `${user_id}_${modelId}.glb`);
  const modelPathusdz = path.join(uploadsDir, `${user_id}_${modelId}.usdz`);

  const photoPath = path.join(uploadsDirec, arPhoto.filename);
  if (!fs.existsSync(photoPath)) {
    return next(new ErrorHandler("Uploaded photo not found", 400));
  }

  // Blender script for AR Photo
  const type_name = arPhoto.filename;
  const scriptPath = path.join(__dirname, "scripts", "generate_photo_model.py");

  const command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${photoPath}" "${orientation}" "${border}" "${color}" "${scale}" "${modelPath}" "${modelPathusdz}"`;

  console.log("🖼️ Executing AR Photo Blender command:", command);

  await new Promise((resolve, reject) => {
    const process = exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error("❌ Blender Error:", error, stderr, stdout);
        return reject(new ErrorHandler("Blender AR Photo model generation failed", 500));
      }
      resolve(stdout);
    });

    // Timeout safeguard
    setTimeout(() => {
      process.kill();
      reject(new ErrorHandler("Blender process timeout", 500));
    }, 600000);
  });

  if (!fs.existsSync(modelPath) || !fs.existsSync(modelPathusdz)) {
    return next(new ErrorHandler("Generated AR Photo model not found", 500));
  }

  // ✅ Generate QR Code URL (respect custom_page)
  const qrCodeUrl = custom_page
    ? `${process.env.FRONTEND_URL}user/page/${custom_page}`
    : `${process.env.FRONTEND_URL}ar-text/${modelId}`;

  const qrCodeImage = await QRCode.toDataURL(qrCodeUrl);

  // ✅ Save entry in DB
  const newAR = await ArTypes.create({
    id: modelId,
    type_name,
    ar_type: ar_type,
    orientation,
    border,
    color,
    scale,
    tracking_pixel,
    custom_page,
    user_id,
    qr_code: qrCodeImage,
    model_path: `models/${user_id}_${modelId}.glb`,
    model_usdz: `models/${user_id}_${modelId}.usdz`,
    reference_name,
    content,
    url,
    password,
  });

  res.json({
    success: true,
    message: "AR Photo QR Code created",
    data: newAR,
  });
});
// AR Portal model create
export const generateArPortal = asyncErrors(async (req, res, next) => {
  const { user_id, ar_type, reference_name, content, url, password, custom_page, tracking_pixel } = req.body;
  const arPortal = req.file;

  if (!user_id || !arPortal) {
    return next(new ErrorHandler("User ID and portal image are required", 400));
  }

  const baseDir = path.join(__dirname, "..");
  const uploadsDirec = path.join(baseDir, "uploads");
  if (!fs.existsSync(uploadsDirec)) fs.mkdirSync(uploadsDirec);

  await UpdateModel.destroy({ where: { user_id } });

  const modelId = uuid().replace(/-/g, "").substring(0, 8);
  const modelPath = path.join(uploadsDir, `${user_id}_${modelId}.glb`);
  const modelPathusdz = path.join(uploadsDir, `${user_id}_${modelId}.usdz`);

  // Ensure image exists
  const photoPath = path.join(uploadsDirec, arPortal.filename);
  if (!fs.existsSync(photoPath)) {
    return next(new ErrorHandler("Uploaded portal image not found", 400));
  }

  // Blender Python script
  const scriptPath = path.join(__dirname, "scripts", "generate_portal_model.py");

  // Command for Blender
  const command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${photoPath}" "${modelPath}" "${modelPathusdz}"`;

  // Run Blender command
  await new Promise((resolve, reject) => {
    const process = exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error("❌ Blender Portal Error:", error, stderr);
        return reject(new ErrorHandler("AR Portal generation failed", 500));
      }
      resolve(stdout);
    });

    // Timeout safety
    setTimeout(() => {
      process.kill();
      reject(new ErrorHandler("AR Portal Blender process timeout", 500));
    }, 600000);
  });

  // Check file outputs
  if (!fs.existsSync(modelPath) || !fs.existsSync(modelPathusdz)) {
    return next(new ErrorHandler("Generated AR Portal model not found", 500));
  }

  const qrCodeUrl = custom_page
    ? `${process.env.FRONTEND_URL}user/page/${custom_page}`
    : `${process.env.FRONTEND_URL}ar-text/${modelId}`;
  const qrCodeImage = await QRCode.toDataURL(qrCodeUrl);

  const newAR = await ArTypes.create({
    id: modelId,
    type_name: arPortal.filename,
    ar_type: ar_type,
    user_id,
    reference_name,
    content,
    url,
    password,
    tracking_pixel,
    custom_page,
    qr_code: qrCodeImage,
    model_path: `models/${user_id}_${modelId}.glb`,
    model_usdz: `models/${user_id}_${modelId}.usdz`,
  });

  res.json({
    success: true,
    message: "AR Portal QR Code created successfully",
    data: newAR,
  });
});
// AR Logo model create
export const generateArLogo = asyncErrors(async (req, res, next) => {
  const { depth, gloss, scale, orientation, overlay, user_id, ar_type, reference_name,
    content,
    url,
    password,
    tracking_pixel,
    custom_page, } = req.body;
  const logoFile = req.file;

  if (!user_id) return next(new ErrorHandler("User ID is required", 400));
  if (!logoFile) return next(new ErrorHandler("Logo SVG file is required", 400));

  const baseDir = path.join(__dirname, "..");
  const uploadsDirec = path.join(baseDir, "uploads");
  const modelId = uuid().replace(/-/g, "").substring(0, 8);
  const modelPath = path.join(uploadsDir, `${user_id}_${modelId}.glb`);
  const modelPathUsdz = path.join(uploadsDir, `${user_id}_${modelId}.usdz`);
  const logoPath = path.join(uploadsDirec, logoFile.filename);

  // Verify SVG file exists
  if (!fs.existsSync(logoPath)) {
    return next(new ErrorHandler("Uploaded logo not found", 400));
  }

  // Build Blender command
  const scriptPath = path.join(baseDir, "controller", "scripts", "generate_logo_model.py");
  const command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${logoPath}" "${depth}" "${gloss}" "${scale}" "${orientation}" "${overlay}" "${modelPath}" "${modelPathUsdz}"`;

  console.log("🔧 Executing Blender command:", command);

  // Run Blender
  const execPromise = new Promise((resolve, reject) => {
    const blender = exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error("❌ Blender Error:", stderr || error);
        reject(new ErrorHandler("Blender model generation failed", 500));
      } else {
        resolve(stdout);
      }
    });

    setTimeout(() => {
      blender.kill();
      reject(new ErrorHandler("Blender process timeout", 500));
    }, 600000);
  });

  await execPromise;

  if (!fs.existsSync(modelPath)) return next(new ErrorHandler("GLB not found", 500));
  if (!fs.existsSync(modelPathUsdz)) return next(new ErrorHandler("USDZ not found", 500));

  // Generate QR code
  const qrCodeUrl = custom_page
    ? `${process.env.FRONTEND_URL}user/page/${custom_page}`
    : `${process.env.FRONTEND_URL}ar-text/${modelId}`;
  const qrCodeImage = await QRCode.toDataURL(qrCodeUrl);

  // ✅ Save in DB
  const newAR = await ArTypes.create({
    id: modelId,
    type_name: logoFile.filename,
    depth,
    gloss,
    scale,
    orientation,
    overlay,
    user_id,
    ar_type,
    reference_name,
    content,
    url,
    password,
    tracking_pixel,
    custom_page,
    qr_code: qrCodeImage,
    model_path: `models/${user_id}_${modelId}.glb`,
    model_usdz: `models/${user_id}_${modelId}.usdz`,
  });

  res.json({
    success: true,
    message: "AR Logo generated successfully",
    data: newAR
  });
});
// AR 3d filecreate
export const generate3DModel = asyncErrors(async (req, res, next) => {
  const { user_id, ar_type, reference_name,
    content,
    url,
    password,
    tracking_pixel,
    custom_page, } = req.body;
  const arFile = req.file; // Uploaded 3D file

  if (!user_id) return next(new ErrorHandler("User ID is required", 400));
  if (!arFile) return next(new ErrorHandler("3D file is required", 400));

  const baseDir = path.join(__dirname, "..");
  const uploadsDirec = path.join(baseDir, "uploads");

  const modelId = uuid().replace(/-/g, "").substring(0, 8);
  const inputPath = path.join(uploadsDirec, arFile.filename);
  const modelPath = path.join(uploadsDir, `${user_id}_${modelId}.glb`);
  const modelPathusdz = path.join(uploadsDir, `${user_id}_${modelId}.usdz`);

  if (!fs.existsSync(inputPath))
    return next(new ErrorHandler("Uploaded file not found", 400));

  const scriptPath = path.join(__dirname, "scripts", "convert_3d_files.py");
  const command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${inputPath}" "${modelPath}" "${modelPathusdz}"`;

  // Run Blender conversion
  const execPromise = new Promise((resolve, reject) => {
    const process = exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error("❌ Blender Error:", error, stderr);
        return reject(new ErrorHandler("3D model conversion failed", 500));
      }
      resolve(stdout);
    });

    setTimeout(() => {
      process.kill();
      reject(new ErrorHandler("Blender conversion timeout", 500));
    }, 600000);
  });

  await execPromise;

  if (!fs.existsSync(modelPath))
    return next(new ErrorHandler("GLB not generated", 500));
  if (!fs.existsSync(modelPathusdz))
    return next(new ErrorHandler("USDZ not generated", 500));

  const modelUrl = `models/${user_id}_${modelId}.glb`;
  const modelUrlusdz = `models/${user_id}_${modelId}.usdz`;

  const qrCodeUrl = custom_page
    ? `${process.env.FRONTEND_URL}user/page/${custom_page}`
    : `${process.env.FRONTEND_URL}ar-text/${modelId}`;
  const qrCodeImage = await QRCode.toDataURL(qrCodeUrl);

  // Save to DB (optional)
  const newAR = await ArTypes.create({
    id: modelId,
    type_name: arFile.filename,
    ar_type: ar_type,
    user_id,
    reference_name,
    content,
    url,
    password,
    tracking_pixel,
    custom_page,
    qr_code: qrCodeImage,
    model_path: modelUrl,
    model_usdz: modelUrlusdz
  });

  res.status(200).json({
    success: true,
    message: "3D model converted successfully!",
    data: newAR
  });
});
// AI Code create qr
export const generateAICodeQrCode = asyncErrors(async (req, res, next) => {
  const {
    type_name,
    reference_name,
    user_id,
    ar_type
  } = req.body;

  if (!user_id || !type_name || !ar_type) {
    return next(new ErrorHandler("Required fields are missing", 400));
  }

  if (ar_type !== "AI Code") {
    return next(new ErrorHandler("AR Type mismatch!", 400));
  }

  const modelId = uuid().replace(/-/g, "").substring(0, 8);

  const qrCodeUrl = `${process.env.FRONTEND_URL}ar-text/${modelId}`;
  const qrCodeImage = await QRCode.toDataURL(qrCodeUrl);

  const newAR = await ArTypes.create({
    id: modelId,
    type_name,
    ar_type,
    reference_name,
    user_id,
    qr_code: qrCodeImage
  });

  res.json({
    success: true,
    message: "AI Code QR Code created!",
    data: newAR,
  });
});
// AI Code analyze Image after scan code
const cleanGeminiResponse = (text) => {
  return text
    .replace(/\*\*/g, '')   // remove bold
    .replace(/\*/g, '')     // remove asterisks
    .replace(/\\n/g, ' ')   // remove \n characters
    .replace(/\s+/g, ' ')   // remove extra whitespace
    .trim();
};
export const AnalyzeAiImageAICode = async (req, res) => {
  const { imageBase64, prompt } = req.body;

  if (!imageBase64 || !prompt) {
    return res.status(400).json({ error: 'Image and prompt are required' });
  }

  try {
    const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' }); // or gemini-1.5-pro

    const promptInstruction = `You are an expert visual AI analyst.

Analyze the image carefully and look for the following keyword(s): ${prompt}.

If any of the keywords are found in the image, explain only those matched items in a clear and detailed way. Include what the object is, where it's typically found, its common uses, and any interesting facts about it.

Make sure the explanation is written in natural, clean language without using any formatting symbols like *, **, -, or line breaks. Just return plain readable text in a paragraph format. Do not mention anything that is not present in the image.`

    const result = await model.generateContent({
      contents: [
        {
          role: 'user',
          parts: [
            { text: promptInstruction },
            { inlineData: { mimeType: 'image/jpeg', data: imageBase64.replace(/^data:image\/\w+;base64,/, '') } },
          ],
        },
      ],
    });

    const rawAnalysis = result.response.candidates?.[0]?.content?.parts?.[0]?.text || '';
    const analysis = cleanGeminiResponse(rawAnalysis);

    res.json({
      success: true,
      message: 'Image analyzed successfully with Gemini',
      matched: true,
      analysis,
    });

  } catch (error) {
    console.error('Gemini analysis error:', error);
    return res.status(500).json({ error: 'Gemini analysis failed', details: error.message });
  }
};
// AR Video create
export const generateArVideo = asyncErrors(async (req, res, next) => {
  const {
    user_id,
    ar_type,
    reference_name,
    content,
    url,
    password,
    custom_page,
    tracking_pixel,
  } = req.body;

  const arVideo = req.file;

  if (!user_id || !arVideo) {
    return next(new ErrorHandler("User ID and video file are required", 400));
  }

  // === Base Directories ===
  const baseDir = path.join(__dirname, "..");
  const uploadsDirec = path.join(baseDir, "uploads");
  // const videosDir = path.join(baseDir, "videos");

  if (!fs.existsSync(uploadsDirec)) fs.mkdirSync(uploadsDirec);
  // if (!fs.existsSync(videosDir)) fs.mkdirSync(videosDir);

  // === Unique Model ID ===
  const modelId = uuid().replace(/-/g, "").substring(0, 8);

  const inputPath = path.join(uploadsDirec, arVideo.filename);
  const mp4Path = path.join(uploadsDir, `${user_id}_${modelId}.mp4`);
  const webmPath = path.join(uploadsDir, `${user_id}_${modelId}.webm`);

  // === Check if uploaded video exists ===
  if (!fs.existsSync(inputPath)) {
    return next(new ErrorHandler("Uploaded video not found", 400));
  }

  // === Convert video formats ===
  await new Promise((resolve, reject) => {
    ffmpeg(inputPath)
      .output(mp4Path)
      .videoCodec("libx264")
      .audioCodec("aac")
      .on("end", () => {
        ffmpeg(inputPath)
          .output(webmPath)
          .videoCodec("libvpx-vp9")
          .audioCodec("libvorbis")
          .on("end", () => {
            fs.unlinkSync(inputPath);
            resolve();
          })
          .on("error", (err) => reject(err))
          .run();
      })
      .on("error", (err) => reject(err))
      .run();
  });

  // === Generate QR Code ===
  const qrCodeUrl = custom_page
    ? `${process.env.FRONTEND_URL}user/page/${custom_page}`
    : `${process.env.FRONTEND_URL}ar-video/${modelId}`;

  const qrCodeImage = await QRCode.toDataURL(qrCodeUrl);

  // === Save to DB ===
  const newAR = await ArTypes.create({
    id: modelId,
    type_name: arVideo.filename,
    ar_type,
    user_id,
    reference_name,
    content,
    url,
    password,
    tracking_pixel,
    custom_page,
    qr_code: qrCodeImage,
    model_path: `models/${user_id}_${modelId}.mp4`,
    model_usdz: `models/${user_id}_${modelId}.webm`,
  });

  // === Response ===
  res.json({
    success: true,
    message: "AR Video created successfully",
    data: newAR,
  });
});
// AR face model create
export const generateArFace = asyncErrors(async (req, res, next) => {
  const { user_id, ar_type } = req.body;
  const arImage = req.file;

  if (!user_id || !arImage) {
    return next(new ErrorHandler("User ID and logo file are required", 400));
  }

  const baseDir = path.join(__dirname, "..");
  const uploadsDir = path.join(baseDir, "uploads");
  if (!fs.existsSync(uploadsDir)) fs.mkdirSync(uploadsDir, { recursive: true });

  const modelId = uuid().replace(/-/g, "").substring(0, 8);

  const inputPath = arImage.path;
  const outputFileName = `${user_id}_${modelId}${path.extname(arImage.originalname)}`;
  const outputPath = path.join(uploadsDir, outputFileName);

  fs.renameSync(inputPath, outputPath);

  const qrCodeUrl = `${process.env.FRONTEND_URL}ar-face/${modelId}`;
  const qrCodeImage = await QRCode.toDataURL(qrCodeUrl);

  const newAR = await ArTypes.create({
    id: modelId,
    type_name: "uploads/" + outputFileName,
    ar_type,
    reference_name: "face",
    user_id,
    qr_code: qrCodeImage,
  });

  res.json({
    success: true,
    message: "AR face created successfully",
    data: newAR,
  });
});



export const generateArPlane = asyncErrors(async (req, res, next) => {
  try {
    const { user_id, ratio_x = 1.6, ratio_y = 0.9 } = req.body;
    if (!user_id) return res.status(400).json({ error: "User ID is required" });

    const baseDir = path.join(__dirname, "..");
    const outputFolder = path.join(baseDir, "models");
    if (!fs.existsSync(outputFolder)) fs.mkdirSync(outputFolder);

    const modelId = Date.now();
    const glbPath = path.join(outputFolder, `${user_id}_${modelId}.glb`);
    const usdzPath = path.join(outputFolder, `${user_id}_${modelId}.usdz`);

    const scriptPath = path.join(baseDir, "controller", "scripts", "generate_video_model.py");

    const blenderCommand = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${glbPath}" "${usdzPath}" "${ratio_x}" "${ratio_y}"`;

    console.log("Executing Blender:", blenderCommand);

    exec(blenderCommand, { maxBuffer: 1024 * 500 }, (error, stdout, stderr) => {
      if (error) {
        console.error("Blender Error:", stderr || error);
        return res.status(500).json({ error: "Blender execution failed" });
      }

      if (!fs.existsSync(glbPath)) return res.status(500).json({ error: "GLB not created" });
      if (!fs.existsSync(usdzPath)) console.warn("USDZ not created, check addon");

      res.json({
        success: true,
        message: "AR plane generated",
        data: {
          glb: `/models/${user_id}_${modelId}.glb`,
          usdz: `/models/${user_id}_${modelId}.usdz`
        }
      });
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Server error" });
  }
});



export const generateQrCodes = asyncErrors(async (req, res, next) => {
  const {
    type_name,
    ar_type,
    font,
    color,
    depth,
    gloss,
    scale,
    orientation,
    reference_name,
    content,
    user_id,
    url,
    password,
    tracking_pixel,
    custom_page,
    border,
    overlay
  } = req.body;

  const arPhoto = req.file; // For AR Photo, the image will be in req.file (from form-data)

  if (!user_id || !ar_type) {
    return next(new ErrorHandler("Required fields are missing", 400));
  }

  const baseDir = path.join(__dirname, "..");
  const tempDir = path.join(baseDir, "temp");

  if (!fs.existsSync(tempDir)) {
    fs.mkdirSync(tempDir);
  }

  // 🧹 Clean up previous files for this user
  fs.readdirSync(tempDir)
    .filter(file => file.includes(user_id))
    .forEach(file => fs.unlinkSync(path.join(tempDir, file)));

  await UpdateModel.destroy({ where: { user_id } });


  const modelId = uuid().replace(/-/g, "").substring(0, 8);
  // const modelPath = path.join(tempDir, `${modelId}.glb`);
  // const modelPathusdz = path.join(tempDir, `${modelId}.usdz`);
  const modelPath = path.join(uploadsDir, `${user_id}_${modelId}.glb`);
  const modelPathusdz = path.join(uploadsDir, `${user_id}_${modelId}.usdz`);

  const defaultImage = path.join(__dirname, "..", "uploads", "my-pic.jpg");
  if (!fs.existsSync(defaultImage)) {
    throw new Error("Default image not found at " + defaultImage);
  }

  let command = "";
  let finalTypeName = "";

  if (ar_type === "AR Text") {
    // if (!type_name || !font || !color || !depth || !gloss || !scale || !orientation) {
    //   return next(new ErrorHandler("Missing fields for AR Text", 400));
    // }

    finalTypeName = type_name;
    const scriptPath = path.join(__dirname, "scripts", "generate_model.py");

    command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${type_name}" "${font}" "${color}" "${depth}" "${gloss}" "${scale}" "${orientation}" "${modelPath}" "${modelPathusdz}"`;

  } else if (ar_type === "AR Photo") {
    if (!arPhoto) return next(new ErrorHandler("Photo is required", 400));

    const photoPath = path.join(baseDir, "uploads", arPhoto.filename);
    if (!fs.existsSync(photoPath)) {
      return next(new ErrorHandler("Uploaded photo not found", 400));
    }

    finalTypeName = arPhoto.filename;
    const scriptPath = path.join(__dirname, "scripts", "generate_photo_model.py");

    command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${photoPath}" "${orientation}" "${border}" "${color}" "${scale}" "${modelPath}" "${modelPathusdz}"`;

  } else if (ar_type === "AR Portal") {
    if (!arPhoto) return next(new ErrorHandler("Photo Portal is required", 400));

    const photoPath = path.join(baseDir, "uploads", arPhoto.filename);
    if (!fs.existsSync(photoPath)) {
      return next(new ErrorHandler("Uploaded photo not found", 400));
    }

    finalTypeName = arPhoto.filename;
    const scriptPath = path.join(__dirname, "scripts", "generate_portal_model.py");

    command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${photoPath}"  "${modelPath}" "${modelPathusdz}"`;

  } else if (ar_type === "AR Face") {
    if (!arPhoto) return next(new ErrorHandler("Face Portal is required", 400));

    const photoPath = path.join(baseDir, "uploads", arPhoto.filename);
    if (!fs.existsSync(photoPath)) {
      return next(new ErrorHandler("Uploaded photo not found", 400));
    }

    finalTypeName = arPhoto.filename;
    const scriptPath = path.join(__dirname, "scripts", "generate_face_filter_model.py");

    command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${photoPath}"  "${modelPath}"`;

  } else if (ar_type === "AR Video") {
    if (!arPhoto) return next(new ErrorHandler("Video is required", 400));

    const photoPath = path.join(baseDir, "uploads", arPhoto.filename);
    if (!fs.existsSync(photoPath)) {
      return next(new ErrorHandler("Uploaded video not found", 400));
    }

    finalTypeName = arPhoto.filename;
    const scriptPath = path.join(__dirname, "scripts", "generate_video_model.py");

    command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${modelPath}" "${photoPath}" "${defaultImage}" "${modelPathusdz}"`;

  } else if (ar_type === "AR Logo") {
    if (!arPhoto) return next(new ErrorHandler("logo is required", 400));

    const logoPath = path.join(baseDir, "uploads", arPhoto.filename);
    if (!fs.existsSync(logoPath)) {
      return next(new ErrorHandler("Uploaded logo not found", 400));
    }

    finalTypeName = arPhoto.filename;
    const scriptPath = path.join(__dirname, "scripts", "generate_logo_model.py");

    command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${logoPath}" "${depth}" "${gloss}" "${scale}" "${orientation}" "${overlay}" "${modelPath}" "${modelPathusdz}"`;

  } else if (ar_type === "3D File") {
    if (!arPhoto) return next(new ErrorHandler("3D file is required", 400));

    const filePath = path.join(baseDir, "uploads", arPhoto.filename);
    if (!fs.existsSync(filePath)) {
      return next(new ErrorHandler("Uploaded logo not found", 400));
    }

    finalTypeName = arPhoto.filename;
    const scriptPath = path.join(__dirname, "scripts", "convert_3d_files.py");

    command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${filePath}" "${modelPath}" "${modelPathusdz}"`;

  } else {
    return next(new ErrorHandler("Invalid AR Type", 400));
  }

  console.log("🔧 Executing Blender command:", command);

  const execPromise = new Promise((resolve, reject) => {
    const process = exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error("❌ Blender Error:", error, stderr, stdout);
        reject(new ErrorHandler("Blender model generation failed", 500));
      } else {
        resolve(stdout);
      }
    });

    setTimeout(() => {
      process.kill();
      reject(new ErrorHandler("Blender process timeout", 500));
    }, 600000); // 10 minutes max
  });

  await execPromise;


  if (!fs.existsSync(modelPath)) {
    return next(new ErrorHandler("Model not found after generation glb", 500));
  }

  if (!fs.existsSync(modelPathusdz)) {
    return next(new ErrorHandler("Model not found after generation usdz", 500));
  }

  // const convertScript = path.join(__dirname, "scripts", "glbConvertToUsdz", "convert.py");
  const modelUrl = `models/${user_id}_${modelId}.glb`;
  const modelUrlusdz = `models/${user_id}_${modelId}.usdz`;

  // const usdzPath = modelPath.replace('.glb', '.usdz');
  // const convertCommand = `"${process.env.BLENDER_PATH}" --background --python "${convertScript}" -- "${modelPath}" "${usdzPath}"`;
  // // const convertCommand = `python "${convertScript}" "${modelPath}" "${usdzPath}"`;
  // console.log(convertCommand, "convert to usdz comm..")
  // // execSync(convertCommand); // Add try/catch around this if needed
  // // const modelUrlUsdz = `models/${modelId}.usdz`; // Now safe to use

  // let modelUrlUsdz;
  // try {
  //   execSync(convertCommand);
  //   modelUrlUsdz = `models/${modelId}.usdz`;
  // } catch (error) {
  //   console.error("❌ USDZ conversion failed:", error);
  //   return next(new ErrorHandler("USDZ conversion failed", 500));
  // }


  const qrCodeUrl = `${process.env.FRONTEND_URL}ar-text/${modelId}`;
  const qrCodeImage = await QRCode.toDataURL(qrCodeUrl);

  const newAR = await ArTypes.create({
    id: modelId,
    type_name: finalTypeName,
    ar_type,
    font: font || null,
    color: color || null,
    depth: depth || null,
    gloss: gloss || null,
    scale: scale || null,
    orientation: orientation || null,
    reference_name,
    content,
    url,
    password,
    tracking_pixel,
    custom_page,
    user_id,
    border,
    qr_code: qrCodeImage,
    model_path: modelUrl,
    model_usdz: modelUrlusdz,
    overlay
  });

  res.json({
    success: true,
    message: `${ar_type} QR Code created`,
    data: {
      id: newAR.id,
      qr_code: qrCodeImage,
      qr_code_url: qrCodeUrl,
      model_path: modelUrl,
      model_usdz: modelUrlusdz
    },
  });
});

// #### QR Code ####
// get single model view
export const arModelView = asyncErrors(async (req, res, next) => {
  try {
    const { id } = req.params;

    const model = await ArTypes.findOne({ where: { id } });
    if (!model) {
      return next(new ErrorHandler("Model not found in the database", 404));
    }
    res.json({
      success: true,
      message: "Model get successfully",
      data: model,
    });
  } catch (error) {
    console.error("Error finding text:", error);
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
});
// get single user models qr codes
export const userArModels = asyncErrors(async (req, res, next) => {
  try {
    const { user_id } = req.params;

    const models = await ArTypes.findAll({ where: { user_id } });
    if (!models) {
      return next(new ErrorHandler("Model not found in the database", 404));
    }
    res.json({
      success: true,
      message: "Models get successfully",
      data: models,
    });
  } catch (error) {
    console.error("Error finding text:", error);
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
});
// single model delete qr
export const qrdelete = asyncErrors(async (req, res, next) => {
  const { id } = req.params;

  const model = await ArTypes.findOne({ where: { id } });

  if (!model) {
    return next(new ErrorHandler("Model not found in the database", 404));
  }

  await model.destroy();

  res.json({
    success: true,
    message: "Model deleted successfully",
  });
});
// qr_scan count
export const trackQrCodeScan = asyncErrors(async (req, res, next) => {
  const { modelId, pageId } = req.params;

  let arItem;

  if (modelId) {
    arItem = await ArTypes.findOne({ where: { id: modelId } });
  } else if (pageId) {
    arItem = await Pages.findOne({ where: { id: pageId } });
  }

  if (!arItem) {
    return next(new ErrorHandler("QR Code not found", 404));
  }

  arItem.scan_count = (arItem.scan_count || 0) + 1;
  await arItem.save();

  res.status(200).json({
    success: true,
    message: "QR Code scan tracked successfully",
    itemType: modelId ? "model" : "page",
    arItem,
  });
});

// custom pages
export const createCustomPage = asyncErrors(async (req, res, next) => {
  const { id } = req.user;
  const {
    reference_name,
    website_url,
    custom_title,
    custom_message,
  } = req.body;

  // File upload fields from multipart/form-data
  const custom_logo = req.files?.custom_logo?.[0]?.filename || null;
  const banner = req.files?.banner?.[0]?.filename || null;

  const user_id = id;

  // Basic validation
  if (!reference_name || !website_url || !custom_title || !custom_message || !user_id) {
    return next(new ErrorHandler("All fields are required!", 400));
  }

  const latestOrder = await Orders.findOne({
    where: { user_id, order_status: "confirmed" },
    order: [["createdAt", "DESC"]],
  });

  console.log(latestOrder, "latestorder..")

  if (!latestOrder) {
    return next(new ErrorHandler("No active subscription/order found for this user", 400));
  }

  const currentPages = await CustomPage.count({ where: { user_id } });

  if (currentPages >= latestOrder.pages) {
    return next(
      new ErrorHandler(
        `You can only create up to ${latestOrder.pages} pages. Upgrade your plan to add more.`,
        400
      )
    );
  }

  const customPage = await CustomPage.create({
    reference_name,
    website_url,
    custom_logo,
    banner,
    custom_title,
    custom_message,
    user_id
  });

  res.status(201).json({
    success: true,
    message: "Custom Page created successfully",
    data: customPage
  });
});

export const allcustomPages = asyncErrors(async (req, res, next) => {
  const user_id = req.user.id;

  if (!user_id) {
    return next(new ErrorHandler("User ID is required", 400));
  }

  const pages = await CustomPage.findAll({
    where: { user_id }
  });

  res.status(200).json({
    success: true,
    count: pages.length,
    data: pages,
  });
})

export const updateCustomPage = asyncErrors(async (req, res, next) => {
  const { id } = req.params;
  const user_id = req.user.id;

  const page = await CustomPage.findOne({ where: { id, user_id } });
  if (!page) {
    return next(new ErrorHandler("Custom page not found", 404));
  }

  // Extract new data from request
  const {
    reference_name,
    website_url,
    custom_title,
    custom_message,
  } = req.body;

  const newLogo = req.files?.custom_logo?.[0]?.filename || null;
  const newBanner = req.files?.banner?.[0]?.filename || null;

  if (newLogo && page.custom_logo) {
    const oldLogoPath = path.join("uploads", page.custom_logo);
    if (fs.existsSync(oldLogoPath)) fs.unlinkSync(oldLogoPath);
  }

  if (newBanner && page.banner) {
    const oldBannerPath = path.join("uploads", page.banner);
    if (fs.existsSync(oldBannerPath)) fs.unlinkSync(oldBannerPath);
  }

  // Update page
  await page.update({
    reference_name: reference_name || page.reference_name,
    website_url: website_url || page.website_url,
    custom_title: custom_title || page.custom_title,
    custom_message: custom_message || page.custom_message,
    custom_logo: newLogo || page.custom_logo,
    banner: newBanner || page.banner,
  });

  res.status(200).json({
    success: true,
    message: "Custom page updated successfully",
    data: page,
  });
});

export const deleteCustomPage = asyncErrors(async (req, res, next) => {
  const { id } = req.params;
  const user_id = req.user.id;

  const page = await CustomPage.findOne({ where: { id, user_id } });
  if (!page) {
    return next(new ErrorHandler("Custom page not found", 404));
  }

  // Delete files if exist
  if (page.custom_logo) {
    const logoPath = path.join("uploads", page.custom_logo);
    if (fs.existsSync(logoPath)) fs.unlinkSync(logoPath);
  }

  if (page.banner) {
    const bannerPath = path.join("uploads", page.banner);
    if (fs.existsSync(bannerPath)) fs.unlinkSync(bannerPath);
  }

  // Delete page
  await page.destroy();

  res.status(200).json({
    success: true,
    message: "Custom page deleted successfully",
  });
});

export const getSingleCustomPage = asyncErrors(async (req, res, next) => {
  const { id } = req.params;
  const user_id = req.user.id;

  const page = await CustomPage.findOne({ where: { id, user_id } });

  if (!page) {
    return next(new ErrorHandler("Custom page not found", 404));
  }

  // Step 2: Find all logs related to this page
  const logs = await ScanLog.findAll({
    where: { custom_page_id: id },
    order: [["createdAt", "DESC"]],
  });

  res.status(200).json({
    success: true,
    data: {
      page,
      logs,
    },
  });
});


// tracking pixel
export const createTrackingPixel = asyncErrors(async (req, res, next) => {
  const { id } = req.user;
  const {
    provider,
    name,
    code
  } = req.body;

  const user_id = id;

  // Basic validation
  if (!provider || !name || !code || !user_id) {
    return next(new ErrorHandler("All fields are required!", 400));
  }

  const tracking = await TrackingPixel.create({
    provider,
    name,
    code,
    user_id
  });

  res.status(200).json({
    success: true,
    message: "Tracking add successfully",
    data: tracking
  });
});

export const allTrackingPixel = asyncErrors(async (req, res, next) => {
  const user_id = req.user.id;

  if (!user_id) {
    return next(new ErrorHandler("User ID is required", 400));
  }

  const pixels = await TrackingPixel.findAll({
    where: { user_id }
  });

  res.status(200).json({
    success: true,
    count: pixels.length,
    data: pixels,
  });
})

export const deleteTrackingPixel = asyncErrors(async (req, res, next) => {
  const { pixel_id } = req.params;

  const pixel = await TrackingPixel.findOne({ where: { id: pixel_id } });

  if (!pixel) {
    return next(new ErrorHandler("pixel not found in the database", 404));
  }

  await pixel.destroy();

  res.json({
    success: true,
    message: "pixel deleted successfully",
  });
});

export const saveScanLog = asyncErrors(async (req, res, next) => {
  try {
    const { page_id } = req.params;

    let ip = req.headers["x-forwarded-for"] || req.socket.remoteAddress;
    if (ip === "::1" || ip === "127.0.0.1") ip = "66.249.66.1";

    let geo = geoip.lookup(ip);
    let country = geo?.country || "Unknown";
    let city = geo?.city || "Unknown";

    if (city === "Unknown") {
      const { data } = await axios.get(`https://ipwho.is/${ip}`);
      if (data.success) {
        country = data.country || country;
        city = data.city || city;
      }
    }

    const ua = new UAParser(req.headers["user-agent"]);
    const browser = ua.getBrowser().name || "Other";
    const os = ua.getOS().name || "Other";
    const deviceType = ua.getDevice().type;
    const device = deviceType ? deviceType : "Desktop";

    const custom_page = await CustomPage.findOne({ where: { id: page_id } });
    if (!custom_page) {
      return next(new ErrorHandler("custom_page not found in the database", 404));
    }

    const existingScan = await ScanLog.findOne({
      where: {
        custom_page_id: page_id,
        ip_address: ip,
        createdAt: { [Op.gte]: new Date(Date.now() - 24 * 60 * 60 * 1000) },
      },
    });

    if (!existingScan) {
      await ScanLog.create({
        custom_page_id: page_id,
        device,
        browser,
        os,
        ip_address: ip,
        country,
        city,
      });
    }

    res.status(200).json({ success: true });
  } catch (err) {
    next(new ErrorHandler(err.message, 500));
  }
});






