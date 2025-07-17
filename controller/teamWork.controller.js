import { asyncErrors } from "../middleware/asyncErrors.js";
import ErrorHandler from "../middleware/error.js";
import { TeamMember } from "../model/teamMembers.model.js";
import crypto from "crypto";
import bcrypt from "bcrypt";
import { Users } from "../model/user.model.js";
import nodemailer from "nodemailer";

export const inviteTeamMember = asyncErrors(async (req, res, next) => {
    const owner_id = req.user.id;
    try {
        const { member_email } = req.body;

        if (!member_email) {
            return next(new ErrorHandler("Member Email are required", 400));
        }

        let existingUser = await Users.findOne({ where: { email: member_email } });
        let generatedPassword = crypto.randomBytes(4).toString("hex");
        let hashedPassword = await bcrypt.hash(generatedPassword, 10);

        let newUser;
        if (!existingUser) {
            newUser = await Users.create({
                user_name: member_email.split("@")[0],
                email: member_email,
                password: hashedPassword,
                role: "team_member",
            });
        } else {
            return next(new ErrorHandler("user already register!", 400));
        }

        // Add to team_members table
        const teamMember = await TeamMember.create({
            owner_id,
            member_id: newUser.id,
            member_email,
            status: "accepted",
        });

        // Send Email
        const transporter = nodemailer.createTransport({
            service: "gmail",
            auth: {
                user: process.env.USER_EMAIL,
                pass: process.env.APP_PASSWORD,
            },
        });

        const mailOptions = {
            from: process.env.USER_EMAIL,
            to: member_email,
            subject: "You have been invited to join a team",
            html: `
    <p>Hello,</p>
    <p>You have been invited to join a team on our platform.</p>
    <p><strong>Here are your login credentials:</strong></p>
    <ul>
      <li><strong>Email:</strong> ${member_email}</li>
      <li><strong>Password:</strong> ${generatedPassword}</li>
    </ul>
    <p>Please <a href="${process.env.FRONTEND_URL}/login" target="_blank">click here to login</a>.</p>
    <p>Thank you.</p>
  `
        };

        transporter.sendMail(mailOptions, (error, info) => {
            if (error) {
                console.log("Email send error:", error);
            } else {
                console.log("Invite Email sent:", info.response);
            }
        });

        return res.status(200).json({
            success: true,
            message: "Team member invited & account created",
            teamMember
        });

    } catch (error) {
        return res.status(500).json({ success: false, message: error.message });
    }
});

export const getTeamMembers = asyncErrors(async (req, res, next) => {
    try {
        const { owner_id } = req.params;
        if (owner_id) {
            return next(new ErrorHandler("Owner-id not found", 404));
        }
        const team = await TeamMember.findAll({ where: { owner_id } });
        return res.status(200).json({ success: true, data: team });
    } catch (error) {
        return res.status(500).json({ success: false, message: error.message });
    }
});

export const removeTeamMember = asyncErrors(async (req, res, next) => {
    const { member_id } = req.params;
    if (!member_id) return next(new ErrorHandler("member id not found", 404));
    const member = await TeamMember.findOne({ where: { id: member_id } });
    if (!member) return next(new ErrorHandler("Member not found", 404));
    await member.destroy();
    return res.status(200).json({ success: true, message: "Member removed" });
});
