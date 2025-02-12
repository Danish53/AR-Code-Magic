import express from "express";
import dotenv from "dotenv";
import cors from "cors";
import session from "express-session";
import cookieParser from "cookie-parser";
import compression from "compression";
import { dbConnection } from "./database/dbConnction.js";
import { syncAllTables } from "./syncAllTables/syncAllTables.js";
import { errorMiddleware } from "./middleware/error.js";
import userRouter from "./router/user.router.js";
import adminRouter from "./router/admin.router.js";
// import stripe from "stripe";

const app = express();
dotenv.config({ path: ".env" });

app.use(
  cors({
    origin: "*",
    methods: ["GET", "PUT", "DELETE", "POST", "PATCH"],
    credentials: true,
  })
);

app.use(cookieParser());
app.use(express.json());
app.use(compression());
app.use(express.urlencoded({ limit: "16kb", extended: true }));
app.use(express.static("public"));
app.use('/uploads', express.static('uploads'));

app.use(
  session({
    secret: "dhfhheewwqqh84883ddnewead", 
    resave: false,
    saveUninitialized: true,
    cookie: { secure: false },
  })
);

app.get("/", function (req, res) {
  res.sendFile(__dirname + "/index.html");
});

//routes 
app.get("/test", function (req, res) {
  res.send("Working Api on this server cors!");
});
app.get("/api/syncAllTables", syncAllTables);
app.use("/api/v1/user", userRouter);
app.use("/api/admin", adminRouter);

dbConnection();
app.use(errorMiddleware);

export default app; 
