import QRCode from "qrcode";
import { v4 as uuid } from "uuid";
import { asyncErrors } from "../middleware/asyncErrors.js";
import path from "path";
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { exec, execSync } from 'child_process';
// import { spawn } from 'child_process';
import ErrorHandler from "../middleware/error.js";
import { ArTypes } from "../model/arTypes.model.js";
import fs from 'fs';
import { UpdateModel } from "../model/tempUpdateModel.model.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// let glbPath = path.join(__dirname, "output", "147e4f26.glb");

const baseDir = path.join(__dirname, "..");
const uploadsDir = path.join(baseDir, "output");

// ar text model
export const updatedModel = async (req, res, next) => {
  const { type_name, font, color, depth, gloss, scale, orientation, user_id } = req.body;

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
    console.log("✅ Font Path Found:", fontPath);

    // **Generate Model Path**
    const modelId = uuid().replace(/-/g, "").substring(0, 8);
    const baseDir = path.join(__dirname, "..");
    const uploadsDir = path.join(baseDir, "temp");

    const model_path = path.join(uploadsDir, `${user_id}_${modelId}.glb`);
    const model_usdz = path.join(uploadsDir, `${user_id}_${modelId}.usdz`);
    const scriptPath = path.join(__dirname, "scripts", "generate_model.py");

    // **Run Blender Command**
    const command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${type_name}" "${fontPath}" "${color}" "${depth}" "${gloss}" "${scale}" "${orientation}" "${model_path}" "${model_usdz}"`;

    console.log(command, "commmmmmm,,,,,,,,,,");

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
    // const usdzPath = model_path.replace('.glb', '.usdz');
    // const convertCommand = `usd_from_gltf "${model_path}" "${usdzPath}"`;
    // execSync(convertCommand); // Add try/catch around this if needed

    // const modelUrlUsdz = `models/${modelId}.usdz`; // Now safe to use



    // **Save to Database**
    const newModel = await UpdateModel.create({
      id: modelId,
      user_id,
      type_name,
      model_path: modelUrl,
      // model_usdz: modelUrlUsdz
    });

    req.getIo().emit("modelUpdated", { id: modelId, model_path: modelUrl });

    res.json({
      success: true,
      message: "Model created successfully",
      data: {
        id: newModel.id,
        model_path: modelUrl,
      },
    });
  } catch (error) {
    console.error("❌ Error:", error);
    res.status(error.status || 500).json({ error: error.message || "Internal server error" });
  }
};
// ar photo Model
export const createPhotoModel = async (req, res, next) => {
  const { orientation, border, color, scale, user_id } = req.body;
  const type_name = req.file?.filename; // 📸 Get uploaded file from multer

  if (!type_name || !user_id) {
    return res.status(400).json({ error: "Required fields are missing" });
  }

  try {
    // **Find Photo Path**
    const photosDir = path.join(__dirname, "..", "uploads");
    // console.log(photosDir, "......dirphoto")
    const photoPath = path.join(photosDir, type_name);

    if (!fs.existsSync(photoPath)) {
      return res.status(400).json({ error: "Photo not found!" });
    }

    console.log("✅ Photo Path Found:", photoPath);

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

    // **Save to Database**
    const newPhotoModel = await UpdateModel.create({
      id: modelId,
      user_id,
      type_name,
      model_path: modelUrl,
    });

    req.getIo().emit("photoModelUpdated", { id: modelId, model_path: modelUrl });

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
  const { user_id } = req.body;
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
// ar face model
export const createFaceModel = async (req, res, next) => {
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

  let modelPath;

  try {
    const photoPath = path.join(__dirname, "..", "uploads", type_name);
    const modelId = uuid().replace(/-/g, "").substring(0, 8);

    // Create temp directory if it doesn't exist
    const tempDir = path.join(__dirname, "..", "temp");
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true });
    }

    modelPath = path.join(tempDir, `${user_id}_${modelId}.glb`);
    const scriptPath = path.join(__dirname, "scripts", "generate_face_filter_model.py");

    // Verify Blender path exists
    if (!process.env.BLENDER_PATH || !fs.existsSync(process.env.BLENDER_PATH)) {
      throw new Error("Blender executable not found at configured path");
    }

    // Verify script exists
    if (!fs.existsSync(scriptPath)) {
      throw new Error(`Python script not found at ${scriptPath}`);
    }

    const command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${photoPath}" "${modelPath}"`;
    console.log("🔧 Running Blender Command:", command);

    const timeout = 600000; // 10 minutes
    const { stdout, stderr } = await new Promise((resolve, reject) => {
      const execProcess = exec(command, (error, stdout, stderr) => {
        if (error) {
          reject({
            error: error,
            stdout: stdout,
            stderr: stderr
          });
        } else {
          resolve({ stdout, stderr });
        }
      });

      setTimeout(() => {
        execProcess.kill();
        reject(new Error("Blender process timed out after 10 minutes"));
      }, timeout);
    });

    console.log("Blender stdout:", stdout);
    console.error("Blender stderr:", stderr);

    // Additional check - wait briefly if file is being written
    let attempts = 0;
    while (!fs.existsSync(modelPath) && attempts < 5) {
      await new Promise(resolve => setTimeout(resolve, 500));
      attempts++;
    }

    if (!fs.existsSync(modelPath)) {
      console.error("Expected output file not found:", modelPath);
      console.error("Directory contents:", fs.readdirSync(tempDir));
      throw new Error("Generated face model file not found after Blender execution");
    }

    // Verify the GLB file has content
    const stats = fs.statSync(modelPath);
    if (stats.size === 0) {
      fs.unlinkSync(modelPath);
      throw new Error("Generated GLB file is empty (0 bytes)");
    }

    if (!fs.existsSync(modelPath)) {
      return res.status(500).json({ error: "Generated model file not found" });
    }

    const modelUrl = `models/${modelId}.glb`;

    const newFaceModel = await UpdateModel.create({
      id: modelId,
      user_id,
      type_name,
      model_path: modelUrl,
    });

    // req.getIo().emit("photoModelUpdated", { id: modelId, model_path: modelUrl });

    res.json({
      success: true,
      message: "face model created successfully",
      data: {
        id: newFaceModel.id,
        model_path: modelUrl,
      },
    });

  } catch (error) {
    console.error("❌ Full Error Details:", {
      message: error.message,
      stdout: error.stdout,
      stderr: error.stderr,
      stack: error.stack
    });

    // Clean up any partial files
    if (modelPath && fs.existsSync(modelPath)) {
      try {
        fs.unlinkSync(modelPath);
      } catch (cleanupError) {
        console.error("Failed to clean up temp file:", cleanupError);
      }
    }

    res.status(500).json({
      error: "AR model generation failed",
      details: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
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

    const command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${modelPath}" "${videoPath}"`;
    console.log("Executing Blender command:", command);

    const timeout = 600000;

    const execPromise = new Promise((resolve, reject) => {
      const execProcess = exec(command, (error, stdout, stderr) => {
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
// ar logo model
export const createARLogoModel = async (req, res, next) => {
  const { user_id, depth, gloss, scale, orientation, overlay } = req.body;
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

    req.getIo().emit("photoModelUpdated", { id: modelId, model_path: modelUrl });

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


// ar object model 
export const generateObjectModel = async (req, res) => {
  const { user_id } = req.body;
  const videoFile = req.file;

  if (!videoFile || !user_id) {
    return res.status(400).json({ error: "Missing required fields" });
  }

  try {
    const modelId = uuid().replace(/-/g, '').substring(0, 8);
    const outputDir = path.join(__dirname, '../temp');
    const outputPath = path.join(outputDir, `${user_id}_${modelId}.glb`);
    const videoPath = path.join(videoFile.destination, videoFile.filename);

    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    const scriptPath = path.join(__dirname, './scripts/generate_object_model.py');
    const command = `"${process.env.PYTHON_PATH || 'python'}" "${scriptPath}" "${videoPath}" "${outputPath}"`;

    console.log("Running command:", command);

    exec(command, { maxBuffer: 1024 * 1024 * 50 }, async (error, stdout, stderr) => {
      console.log("STDOUT:", stdout);
      if (stderr) console.error("STDERR:", stderr);

      if (error) {
        console.error("Exec error:", error);
        return res.status(500).json({ error: "Model generation failed", details: error.message });
      }

      if (!fs.existsSync(outputPath)) {
        return res.status(500).json({
          error: "Model generation failed",
          details: stderr || stdout || "Unknown error"
        });
      }

      try {
        const modelUrl = `/models/${modelId}.glb`;
        await UpdateModel.create({
          id: modelId,
          user_id,
          model_path: modelUrl,
          type_name: videoFile.originalname
        });

        const publicPath = path.join(__dirname, '../../public/models');
        if (!fs.existsSync(publicPath)) {
          fs.mkdirSync(publicPath, { recursive: true });
        }
        await fs.promises.rename(outputPath, path.join(publicPath, `${modelId}.glb`));
        await fs.promises.unlink(videoPath);

        return res.status(200).json({
          success: true,
          data: {
            id: modelId,
            model_path: modelUrl
          }
        });
      } catch (dbError) {
        console.error("Database error:", dbError);
        if (fs.existsSync(outputPath)) {
          await fs.promises.unlink(outputPath);
        }
        return res.status(500).json({ error: "Failed to save model" });
      }
    });
  } catch (err) {
    console.error("Unexpected error:", err);
    return res.status(500).json({ error: "Internal server error" });
  }
};

export const latestModel = asyncErrors(async (req, res, next) => {
  const glbPath = path.join(uploadsDir, "updated_model.glb");

  if (fs.existsSync(glbPath)) {
    res.json({ success: true, modelUrl: `http://localhost:${PORT}/models/147e4f26.glb?${Date.now()}` });
  } else {
    res.status(404).json({ success: false, message: "Model not found" });
  }
});

// export const generateQrCodes = asyncErrors(async (req, res, next) => {
//   const {
//     type_name,
//     ar_type,
//     font,
//     color,
//     depth,
//     gloss,
//     scale,
//     orientation,
//     reference_name,
//     content,
//     user_id,
//     url,
//     password,
//     tracking_pixel,
//     custom_page,
//   } = req.body;

//   // Validate required fields
//   if (!type_name || !user_id || !ar_type) {
//     return next(new ErrorHandler("Required fields are missing", 400));
//   }

//   const baseDir = path.join(__dirname, "..");
//   const tempDir = path.join(baseDir, "temp");

//   if (fs.existsSync(tempDir)) {
//     const files = fs.readdirSync(tempDir); // Read all files in temp folder

//     files.forEach((file) => {
//       if (file.includes(user_id)) {  // ✅ Delete only user-specific files
//         const filePath = path.join(tempDir, file);
//         fs.unlinkSync(filePath); // Delete file
//         console.log(`Deleted temp file: ${filePath}`);
//       }
//     });
//   }

//   // 🟢 STEP 3: Remove entries from DB
//   await UpdateModel.destroy({ where: { user_id } });
//   console.log(`Deleted database entries for user: ${user_id}`);


//   try {
//     const modelId = uuid().replace(/-/g, "").substring(0, 8);
//     const baseDir = path.join(__dirname, "..");
//     const uploadsDir = path.join(baseDir, "output");
//     const model_path = path.join(uploadsDir, `${modelId}.glb`);

//     const scriptPath = path.join(__dirname, "scripts", "generate_model.py");

//     // Call Blender script to generate 3D model
//     const command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${type_name}" "${font}" "${color}" "${depth}" "${gloss}" "${scale}" "${orientation}" "${model_path}"`;
//     console.log("......comand", command)
//     exec(command, async (error, stdout, stderr) => {
//       if (error) {
//         console.error("Error generating 3D model:", error);
//         console.error("Blender Stderr:", stderr);
//         return next(new ErrorHandler("Error generating 3D model", 500));
//       }

//       if (!fs.existsSync(model_path)) {
//         console.error("Model file not found:", model_path);
//         return next(new ErrorHandler("Model file not found", 500));
//       }

//       const qrCodeUrl = `${process.env.FRONTEND_URL}ar-text/${modelId}`;
//       const qrCodeImage = await QRCode.toDataURL(qrCodeUrl);

//       const modelUrl = `models/${modelId}.glb`;

//       const newText = await ArTypes.create({
//         id: modelId,
//         type_name,
//         ar_type,
//         font,
//         color,
//         depth,
//         gloss,
//         scale,
//         orientation,
//         reference_name,
//         content,
//         url,
//         password,
//         tracking_pixel,
//         custom_page,
//         user_id,
//         qr_code: qrCodeImage,
//         model_path: modelUrl
//       });

//       res.json({
//         success: true,
//         message: "QR Code generated successfully",
//         data: {
//           id: newText.id,
//           qr_code: qrCodeImage,
//           qr_code_url: qrCodeUrl,
//           model_path: modelUrl
//         },
//       });
//     });
//   } catch (error) {
//     console.error("Error generating QR Code:", error);
//     return next(new ErrorHandler("internal server error!", 500));
//   }
// });

// qr code and model generate
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

  }else if (ar_type === "AR Face") {
    if (!arPhoto) return next(new ErrorHandler("Face Portal is required", 400));

    const photoPath = path.join(baseDir, "uploads", arPhoto.filename);
    if (!fs.existsSync(photoPath)) {
      return next(new ErrorHandler("Uploaded photo not found", 400));
    }

    finalTypeName = arPhoto.filename;
    const scriptPath = path.join(__dirname, "scripts", "generate_face_filter_model.py");

    command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${photoPath}"  "${modelPath}"`;

  }else if (ar_type === "AR Video") {
    if (!arPhoto) return next(new ErrorHandler("Video is required", 400));

    const photoPath = path.join(baseDir, "uploads", arPhoto.filename);
    if (!fs.existsSync(photoPath)) {
      return next(new ErrorHandler("Uploaded video not found", 400));
    }

    finalTypeName = arPhoto.filename;
    const scriptPath = path.join(__dirname, "scripts", "generate_video_model.py");

    command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${modelPath}" "${photoPath}"`;

  } else if (ar_type === "AR Logo") {
    if (!arPhoto) return next(new ErrorHandler("logo is required", 400));

    const logoPath = path.join(baseDir, "uploads", arPhoto.filename);
    if (!fs.existsSync(logoPath)) {
      return next(new ErrorHandler("Uploaded logo not found", 400));
    }

    finalTypeName = arPhoto.filename;
    const scriptPath = path.join(__dirname, "scripts", "generate_logo_model.py");

   command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${logoPath}" "${depth}" "${gloss}" "${scale}" "${orientation}" "${overlay}" "${modelPath}" "${modelPathusdz}"`;

  } else {
    return next(new ErrorHandler("Invalid AR Type", 400));
  }

  console.log("🔧 Executing Blender command:", command);

  const execPromise = new Promise((resolve, reject) => {
    const process = exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error("❌ Blender Error:", error, stderr);
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

    const models = await ArTypes.findOne({ where: { user_id } });
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


