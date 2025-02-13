import QRCode from "qrcode";
import { v4 as uuid } from "uuid";
import { asyncErrors } from "../middleware/asyncErrors.js";
import ErrorHandler from "../middleware/error.js";
// import { Users } from "../model/user.model.js";
import { ArTypes } from "../model/arTypes.model.js";

// Create QR Code
export const generateQrCodes = asyncErrors(async (req, res, next) => {
  try {
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
      user_id = 7,
      url,
      password,
      tracking_pixel,
      custom_page,
    } = req.body;
    if (!type_name || !ar_type) {
      return next(new ErrorHandler("Required fields are missing", 400));
    }
    // const user = await Users.findOne({ where: { id: user_id } });
    // if (!user) {
    //   return next(new ErrorHandler("User not found", 404));
    // }

    const generatedUuid = uuid();
    const qrCodeUrl = `${process.env.BASE_URL || ""}/ar-text/${generatedUuid}`;
    const qrCodeImage = await QRCode.toDataURL(qrCodeUrl);

    const newText = await ArTypes.create({ 
      id: generatedUuid,
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
    });

    res.json({
      success: true,
      message: "QR Code generated successfully",
      data: {
        id: newText.id,
        qr_code: qrCodeImage,
        qr_code_url: qrCodeUrl,
      },
    });
  } catch (error) {
    console.error("Error generating QR Code:", error);
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
});

export const arTextView = asyncErrors(async (req, res, next) => {
  try {
    const { id } = req.params; 

    const text = await ArTypes.findOne({ where: { id } });
    if (!text) {
      return next(new ErrorHandler("Text not found in the database", 404));
    }
    res.json({
      success: true,
      message: "Text get successfully",
      data: text,
    });
  } catch (error) {
    console.error("Error finding text:", error);
    res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
});
