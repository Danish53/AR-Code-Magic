import { asyncErrors } from "../middleware/asyncErrors.js";
import { StripeKeys } from "../model/stripeKeys.model.js";
import Stripe from 'stripe';
import { Users } from "../model/user.model.js";

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

