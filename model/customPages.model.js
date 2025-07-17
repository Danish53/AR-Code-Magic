import { DataTypes } from "sequelize";
import { sequelize } from "../database/dbConnction.js";

const CustomPage = sequelize.define("custompages", {
    id: {
        type: DataTypes.INTEGER,
        autoIncrement: true,
        primaryKey: true,
    },
    reference_name: {
        type: DataTypes.STRING,
        allowNull: false,
    },
    website_url: {
        type: DataTypes.STRING,
        allowNull: false,
        validate: {
            isUrl: true,
        },
    },
    custom_logo: {
        type: DataTypes.STRING,
        allowNull: true,
    },
    banner: {
        type: DataTypes.STRING,
        allowNull: true,
    },
    custom_title: {
        type: DataTypes.STRING,
        allowNull: true,
    },
    custom_message: {
        type: DataTypes.STRING(140),
        allowNull: true,
    },
    user_id: {
        type: DataTypes.INTEGER,
        allowNull: false,
    },
}, {
    timestamps: true,

});

export { CustomPage };
