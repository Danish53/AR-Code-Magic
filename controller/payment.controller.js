import { asyncErrors } from "../middleware/asyncErrors.js";
import { StripeKeys } from "../model/stripeKeys.model.js";
import Stripe from 'stripe';
import moment from "moment";
import { Users } from "../model/user.model.js";
import { Orders } from "../model/orders.model.js";
import { Packages } from "../model/packages.model.js";
import crypto from "crypto";

export const stripeKeyUpdate = asyncErrors(async (req, res, next) => {
  const { stripe_client_id, stripe_secret, stripe_status } = req.body;

  try {
    let key = await StripeKeys.findOne({
      where: { stripe_client_id },
    });

    if (key) {
      key.stripe_secret = stripe_secret;
      key.stripe_status = stripe_status;
      await key.save();

      return res.status(200).json({
        success: true,
        message: "Key updated successfully",
        key,
      });
    } else {
      key = await StripeKeys.create({
        stripe_client_id,
        stripe_secret,
        stripe_status,
      });

      return res.status(201).json({
        success: true,
        message: "Key created successfully",
        key,
      });
    }
  } catch (error) {
    console.error(error);
    res
      .status(500)
      .json({ success: false, message: "Error processing request" });
  }
});
export const stripeKeyGet = asyncErrors(async (req, res, next) => {
  try {
    const key = await StripeKeys.findOne({
      where: { stripe_status: "enable" },
    });

    if (!key) {
      return res.status(404).json({ success: false, message: "Key not found" });
    }

    res.status(200).json({
      success: true,
      message: "Key fetched successfully",
      key,
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ success: false, message: "Error fetching key" });
  }
});

// stripe payment gateway
// export const stripePayment = asyncErrors(async (req, res, next) => {
//   const { token, amount } = req.body;

//   if (!token || !amount) {
//     return res.status(400).json({ success: false, message: "Missing payment details" });
//   }

//   try {
//     const key = await StripeKeys.findOne({
//       where: { stripe_status: "enable" },
//     });

//     if (!key) {
//       return res.status(404).json({ success: false, message: "Stripe key not found or not enabled" });
//     }

//     const user = await Users.findOne({
//       where: { id: req.user.id },
//     });

//     const stripe = Stripe(key.stripe_secret);

//     const paymentIntent = await stripe.paymentIntents.create({
//       amount: parseInt(amount, 10) * 100, 
//       currency: "usd",
//       payment_method: token,
//       confirm: true,
//       payment_method_types: ["card"],
//       description: "Payment for a qr code",
//       receipt_email: user.email, 
//       return_url: "https://example.com/return",
//       metadata: {
//         order_id: "order_123",
//         user_id: user.id,
//       },
//     });

//     res.status(200).json({
//       success: true,
//       message: "Payment successful",
//       paymentIntent,
//     });
//   } catch (error) {
//     console.error('Stripe Payment Error:', error);
//     if (error.type === 'StripeCardError') {
//       res.status(400).json({ success: false, message: 'Card error: ' + error.message });
//     } else {
//       res.status(500).json({ success: false, message: 'Error processing payment' });
//     }
//   }
// });

// controllers/paymentController.js stripe
// export const createPaymentAndOrder = async (req, res) => {
//   try {
//     const { user_id, package_id, payment_method_id } = req.body;

//     const stripeKeyRecord = await StripeKeys.findOne();
//     if (!stripeKeyRecord) {
//       return res.status(500).json({ success: false, message: "Stripe secret key not found" });
//     }
//     const stripe = new Stripe(stripeKeyRecord.stripe_secret);
//     console.log(stripe, "stripe key");

//     const user = await Users.findOne({ where: { id: user_id } });
//     if (!user) {
//       return res.status(404).json({ success: false, message: "User not found" });
//     }

//     const selectedPackage = await Packages.findOne({ where: { id: package_id } });
//     if (!selectedPackage) {
//       return res.status(404).json({ success: false, message: "Package not found" });
//     }

//     const paymentIntent = await stripe.paymentIntents.create({
//       amount: selectedPackage.package_price * 100, // in cents
//       currency: "usd",
//       payment_method: payment_method_id,
//       confirm: true,
//       receipt_email: user.email,
//       automatic_payment_methods: {
//         enabled: true,
//         allow_redirects: 'never',
//       },
//     });

//     const newOrder = await Orders.create({
//       user_id,
//       package_id: selectedPackage.id,
//       package_name: selectedPackage.package_name,
//       package_price: selectedPackage.package_price,
//       package_duration: selectedPackage.duration,
//       order_status: "confirmed",
//       payment_id: paymentIntent.id,
//       payment_method: paymentIntent.payment_method_types[0],
//       order_start_date: moment().format("YYYY-MM-DD"),
//       order_end_date: moment().add(selectedPackage.duration, "days").format("YYYY-MM-DD"),
//       ar_codes: selectedPackage.ar_codes.toString(),
//       scans: selectedPackage.scans.toString(),
//       pages: selectedPackage.pages.toString(),
//       tracking: selectedPackage.tracking.toString(),
//     });

//     const updates = {
//       package_id: selectedPackage.id,
//       isTrial: 0
//     };

//     const generateApiKey = () => {
//       return "arcoded_pk_" + crypto.randomBytes(12).toString("hex");
//     };

//     if (!user.api_key) {
//       updates.api_key = generateApiKey();
//     }

//     await Users.update(updates, { where: { id: user_id } });

//     return res.status(200).json({
//       success: true,
//       message: "Payment successful & order created",
//       order: newOrder,
//     });

//   } catch (error) {
//     console.error("Stripe Payment Error:", error.message);
//     return res.status(500).json({
//       success: false,
//       message: "Payment failed",
//       error: error.message,
//     });
//   }
// };

//  Create Stripe Checkout Session
export const createCheckoutSession = async (req, res) => {
  try {
    const { user_id, package_id } = req.body;

    // ✅ Fetch user & package
    const user = await Users.findOne({ where: { id: user_id } });
    if (!user) return res.status(404).json({ success: false, message: "User not found" });

    const selectedPackage = await Packages.findOne({ where: { id: package_id } });
    if (!selectedPackage)
      return res.status(404).json({ success: false, message: "Package not found" });

    const stripeKeyRecord = await StripeKeys.findOne();
    if (!stripeKeyRecord) {
      return res.status(500).json({ success: false, message: "Stripe secret key not found" });
    }
    const stripe = new Stripe(stripeKeyRecord.stripe_secret);

    // ✅ Create a Checkout Session
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ["card"],
      mode: "payment",
      customer_email: user.email,
      line_items: [
        {
          price_data: {
            currency: "usd",
            product_data: {
              name: selectedPackage.package_name,
              description: `
                Package: ${selectedPackage.package_name}
                Pages: ${selectedPackage.pages}
                Tracking: ${selectedPackage.tracking}
                Scans: ${selectedPackage.scans}
                Scans: ${selectedPackage.ar_codes}
                Plan: ${selectedPackage.plan_frequency}
                After payment, your AR Code account will be upgraded automatically.
              `,
            },
            unit_amount: selectedPackage.discount_price * 100,
          },
          quantity: 1,
        },
      ],
      success_url: `${process.env.FRONTEND_URL}/payment-success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.FRONTEND_URL}/payment-cancel`,
      metadata: {
        user_id: user.id.toString(),
        package_id: selectedPackage.id.toString(),
        package_name: selectedPackage.package_name,
        package_title: selectedPackage.package_title,
        package_price: selectedPackage.discount_price.toString(),
        pages: selectedPackage.pages?.toString() || "0",
        tracking: selectedPackage.tracking?.toString() || "0",
        scans: selectedPackage.scans?.toString() || "0",
        ar_codes: selectedPackage.ar_codes?.toString() || "0",
      },
    });

    return res.status(200).json({
      success: true,
      url: session.url,
    });
  } catch (error) {
    console.error("Stripe Session Error:", error.message);
    return res.status(500).json({ success: false, message: error.message });
  }
};

export const verifyPayment = async (req, res) => {
  try {
    const { session_id } = req.body;

    const stripeKeyRecord = await StripeKeys.findOne();
    const stripe = new Stripe(stripeKeyRecord.stripe_secret);

    // Stripe se session fetch karo
    const session = await stripe.checkout.sessions.retrieve(session_id);

    if (session.payment_status === "paid") {
      const user_id = session.metadata.user_id;
      const package_id = session.metadata.package_id;

      const user = await Users.findOne({ where: { id: user_id } });
      const selectedPackage = await Packages.findOne({ where: { id: package_id } });

      // ✅ Order create karo
      const newOrder = await Orders.create({
        user_id,
        package_id: selectedPackage.id,
        package_name: selectedPackage.package_name,
        package_price: selectedPackage.discount_price,
        package_duration: selectedPackage.duration,
        order_status: "confirmed",
        payment_id: session.payment_intent,
        payment_method: "card",
        order_start_date: moment().format("YYYY-MM-DD"),
        order_end_date: moment().add(selectedPackage.duration || 30, "days").format("YYYY-MM-DD"),
        ar_codes: selectedPackage.ar_codes.toString(),
        scans: selectedPackage.scans.toString(),
        pages: selectedPackage.pages.toString(),
        tracking: selectedPackage.tracking.toString(),
      });

      // ✅ User plan update karo
      await Users.update(
        { package_id: selectedPackage.id, isTrial: 0 },
        { where: { id: user_id } }
      );

      return res.status(200).json({ success: true, message: "Payment verified Successfully!", order: newOrder });
    }

    res.status(400).json({ success: false, message: "Payment not completed yet" });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};


