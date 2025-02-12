import jwt from "jsonwebtoken";
import { asyncErrors } from "./asyncErrors.js";
import ErrorHandler from "./error.js";
import { Users } from "../model/user.model.js";

//AUTHENTICATION
export const isAuthenticated = asyncErrors(async (req, res, next) => {
  const token =
    req.cookies.token ||
    (req.headers.authorization && req.headers.authorization.split(" ")[1]);
  if (!token) {
    return next(new ErrorHandler("User is not authenticated!", 400));
  }
  const decoded = jwt.verify(token, process.env.JWT_SECRET_KEY);

  req.user = await Users.findByPk(decoded.id);

  next();
});

//AUTHORIZATION
export const isAuthorized = (...roles) => {
  return (req, res, next) => {
    console.log(req.user);
    if (!roles.includes(req.user.role)) {
      return next(
        new ErrorHandler(
          `User with this role (${req.user.role}) not allowed to access this resource`
        )
      );
    }
    next();
  };
};
