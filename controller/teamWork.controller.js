import { asyncErrors } from "../middleware/asyncErrors.js";
import ErrorHandler from "../middleware/error.js";
import { TeamMember } from "../model/teamMembers.model.js";
import crypto from "crypto";
import bcrypt from "bcrypt";
import { Users } from "../model/user.model.js";
import nodemailer from "nodemailer";
import { Packages } from "../model/packages.model.js";
// import { Packages } from "../model/packages.model.js";

export const inviteTeamMember = asyncErrors(async (req, res, next) => {
    const owner_id = req.user.id;

    try {
        const { member_email } = req.body;

        if (!member_email) {
            return next(new ErrorHandler("Member Email is required", 400));
        }

        const owner = await Users.findOne({
            where: { id: owner_id },
            include: [
                {
                    model: Packages,
                    as: "plan",
                },
            ],
        });

        if (!owner || !owner.plan) {
            return next(
                new ErrorHandler(
                    "You don't have any active plan. Upgrade to invite team members.",
                    403
                )
            );
        }

        if (
            owner.plan.package_name !== "PRO" &&
            owner.plan.package_name !== "STANDARD"
        ) {
            return next(
                new ErrorHandler(
                    "Only Pro and Standard plan users can invite team members.",
                    403
                )
            );
        }

        // ✅ STEP 1: Check existing user
        const existingUser = await Users.findOne({ where: { email: member_email } });
        if (existingUser) {
            return next(new ErrorHandler("User already registered!", 400));
        }

        const generatedPassword = crypto.randomBytes(4).toString("hex");

        const newUser = await Users.create({
            user_name: member_email.split("@")[0],
            email: member_email,
            password: generatedPassword, // plain password, hook will hash it
            role: "team_member",
        });

        const teamMember = await TeamMember.create({
            owner_id,
            member_id: newUser.id,
            member_email,
            status: "accepted",
        });

        // ✅ STEP 5: Setup transporter for Gmail
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
          <li><strong>Password:</strong> 
            <pre style="display:inline; font-size:15px; font-weight:bold; background:#f8f9fa; padding:4px; border-radius:4px;">${generatedPassword}</pre>
          </li>
        </ul>
        <p>Please <a href="${process.env.FRONTEND_URL}/login" target="_blank">click here to login</a>.</p>
        <p>Thank you.</p>
      `,
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
            teamMember,
        });
    } catch (error) {
        console.error("Invite Error:", error);
        return res.status(500).json({ success: false, message: error.message });
    }
});

export const getTeamMembers = asyncErrors(async (req, res, next) => {
    try {
        const owner_id = req.user.id;
        if (!owner_id) {
            return next(new ErrorHandler("Owner-id not found", 404));
        }

        const team = await TeamMember.findAll({ where: { owner_id } });

        // Parse permissions if it's string
        const formattedTeam = team.map(member => {
            let permissions = member.permissions;
            if (typeof permissions === "string") {
                try {
                    permissions = JSON.parse(permissions);
                } catch (err) {
                    permissions = {};
                }
            }
            return {
                ...member.toJSON(),
                permissions,
            };
        });

        return res.status(200).json({ success: true, data: formattedTeam });
    } catch (error) {
        return res.status(500).json({ success: false, message: error.message });
    }
});

export const updateTeamMemberPermissions = asyncErrors(async (req, res, next) => {
    const { member_id } = req.params;
    let { permissions } = req.body;

    if (!member_id) return next(new ErrorHandler("Member ID not provided", 400));
    if (!permissions || typeof permissions !== "object")
        return next(new ErrorHandler("Permissions object is required", 400));

    const member = await TeamMember.findOne({ where: { member_id } });
    if (!member) return next(new ErrorHandler("Team member not found", 404));

    if (member.owner_id !== req.user.id) {
        return next(new ErrorHandler("Not authorized to update this member", 403));
    }

    let currentPermissions = member.permissions;
    if (typeof currentPermissions === "string") {
        currentPermissions = JSON.parse(currentPermissions);
    }

    member.permissions = { ...currentPermissions, ...permissions };
    await member.save();


    return res.status(200).json({
        success: true,
        message: "Permissions updated successfully",
        data: member
    });
});

export const removeTeamMember = asyncErrors(async (req, res, next) => {
    const { member_id } = req.params;
    if (!member_id) return next(new ErrorHandler("member id not found", 404));
    const member = await TeamMember.findOne({ where: { member_id } });
    if (!member) return next(new ErrorHandler("Member not found", 404));
    await member.destroy();
    await Users.update({ role: 'user' }, { where: { id: member.member_id } });
    return res.status(200).json({ success: true, message: "Member removed" });
});
