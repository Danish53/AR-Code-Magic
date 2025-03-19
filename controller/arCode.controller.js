import QRCode from "qrcode";
import { v4 as uuid } from "uuid";
import { asyncErrors } from "../middleware/asyncErrors.js";
import path from "path";
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { exec } from 'child_process';
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

    const model_path = path.join(uploadsDir, `${modelId}.glb`);
    const scriptPath = path.join(__dirname, "scripts", "generate_model.py");

    // **Run Blender Command**
    const command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${type_name}" "${fontPath}" "${color}" "${depth}" "${gloss}" "${scale}" "${orientation}" "${model_path}"`;

    exec(command, async (error, stdout, stderr) => {
      if (error) {
        console.error("❌ Error:", error, stderr);
        return res.status(500).json({ error: "3D model generation failed" });
      }

      if (!fs.existsSync(model_path)) {
        return res.status(500).json({ error: "Generated model file not found" });
      }

      const modelUrl = `models/${modelId}.glb`;

      // **Save to Database**
      const newModel = await UpdateModel.create({
        id: modelId,
        user_id,
        type_name,
        model_path: modelUrl,
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
    });
  } catch (error) {
    console.error("❌ Error:", error);
    res.status(500).json({ error: "Internal server error" });
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
  } = req.body;

  // Validate required fields
  if (!type_name || !user_id || !ar_type) {
    return next(new ErrorHandler("Required fields are missing", 400));
  }

  const baseDir = path.join(__dirname, "..");
    const tempDir = path.join(baseDir, "temp");

  if (fs.existsSync(tempDir)) {
    const files = fs.readdirSync(tempDir); // Read all files in temp folder

    files.forEach((file) => {
      if (file.includes(user_id)) {  // ✅ Delete only user-specific files
        const filePath = path.join(tempDir, file);
        fs.unlinkSync(filePath); // Delete file
        console.log(`Deleted temp file: ${filePath}`);
      }
    });
  }

    // 🟢 STEP 3: Remove entries from DB
    await UpdateModel.destroy({ where: { user_id } });
    console.log(`Deleted database entries for user: ${user_id}`);
  

  try {
    const modelId = uuid().replace(/-/g, "").substring(0, 8);
    const baseDir = path.join(__dirname, "..");
    const uploadsDir = path.join(baseDir, "output");
    const model_path = path.join(uploadsDir, `${modelId}.glb`);

    const scriptPath = path.join(__dirname, "scripts", "generate_model.py"); 

    // Call Blender script to generate 3D model
    const command = `"${process.env.BLENDER_PATH}" --background --python "${scriptPath}" -- "${type_name}" "${font}" "${color}" "${depth}" "${gloss}" "${scale}" "${orientation}" "${model_path}"`;
    console.log("......comand", command)
    exec(command, async (error, stdout, stderr) => {
      if (error) {
        console.error("Error generating 3D model:", error);
        console.error("Blender Stderr:", stderr);
        return next(new ErrorHandler("Error generating 3D model", 500));
      }

      if (!fs.existsSync(model_path)) {
        console.error("Model file not found:", model_path);
        return next(new ErrorHandler("Model file not found", 500));
      }

      const qrCodeUrl = `${process.env.FRONTEND_URL}ar-text/${modelId}`;
      const qrCodeImage = await QRCode.toDataURL(qrCodeUrl);

      const modelUrl = `models/${modelId}.glb`;

      const newText = await ArTypes.create({
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
        qr_code: qrCodeImage,
        model_path: modelUrl
      });

      res.json({
        success: true,
        message: "QR Code generated successfully",
        data: {
          id: newText.id,
          qr_code: qrCodeImage,
          qr_code_url: qrCodeUrl,
          model_path: modelUrl
        },
      });
    });
  } catch (error) {
    console.error("Error generating QR Code:", error);
    return next(new ErrorHandler("internal server error!", 500));
  }
});

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


