import { Users } from "../model/user.model.js";


export const checkApiKey = async (req, res, next) => {
  const key = req.headers['x-api-key'];

  if (!key) {
    return res.status(401).json({ success: false, message: "API key missing" });
  }

  const user = await Users.findOne({ where: { api_key: key } });

  if (!user) {
    return res.status(403).json({ success: false, message: "Invalid API key" });
  }

  req.user = user;
  next();
};
