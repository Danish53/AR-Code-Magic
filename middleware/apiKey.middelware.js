import { Users } from "../model/user.model.js";

export const checkApiKey = async (req, res, next) => {
  try {
    const apiKey = req.query.api_key

    if (!apiKey) {
      return res.status(401).json({ success: false, message: "API Key required!" });
    }

    const user = await Users.findOne({ where: { api_key: apiKey } });

    if (!user) {
      return res.status(403).json({ success: false, message: "Invalid API Key!" });
    }

    req.user = user;
    next();
  } catch (err) {
    return res.status(500).json({ success: false, message: err.message });
  }
};
