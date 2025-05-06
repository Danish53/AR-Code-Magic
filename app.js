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
import path from "path";
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import http from "http";

import { Server } from "socket.io"; 


const app = express();
const server = http.createServer(app);

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

dotenv.config({ path: ".env" });

app.use(
  cors({
    origin: process.env.FRONTEND,
    methods: ["GET", "PUT", "DELETE", "POST", "PATCH"],
    credentials: true,
  })
);

const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"],
  },
});


app.use((req, res, next) => {
  req.getIo = () => io;
  next();
});

io.on("connection", (socket) => {
  console.log("New WebSocket connection:", socket.id);

  socket.on("disconnect", () => {
    console.log("User disconnected:", socket.id);
  });
});


app.use(cookieParser());
app.use(express.json());
app.use(compression());
app.use(express.urlencoded({ limit: "16kb", extended: true }));
app.use(express.static("public"));
app.use('/uploads', express.static('uploads'));
app.use("/models", express.static(path.join(__dirname, "output")));
app.use("/models", express.static(path.join(__dirname, "temp")));


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

server.listen(process.env.PORT || 8000, () => {
  console.log(`Server running on port ${process.env.PORT}`);
});

export default app; 
