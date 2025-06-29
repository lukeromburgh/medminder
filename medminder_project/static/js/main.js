// // static/main.js

// document.addEventListener("DOMContentLoaded", function() {
//   console.log("Sanity check!");

//   // Get Stripe publishable key
//   fetch("/payments/config/")
//     .then((result) => result.json())
//     .then((data) => {
//       // Initialize Stripe.js
//       const stripe = Stripe(data.publicKey);

//       // Event handler
//       document.querySelector("#checkout-button").addEventListener("click", () => {
//         // Get Checkout Session ID
//         fetch("/payments/create-checkout-session/")
//           .then((result) => result.json())
//           .then((data) => {
//             console.log(data);
//             // Redirect to Stripe Checkout
//             return stripe.redirectToCheckout({ sessionId: data.sessionId });
//           })
//           .then((res) => {
//             console.log(res);
//           });
//       });
//     });
// });

// main.js
document.addEventListener("DOMContentLoaded", function() {
  console.log("Sanity check!");

  fetch("/payments/config/")
    .then((result) => result.json())
    .then((data) => {
      const stripe = Stripe(data.publicKey);

      const checkoutBtn = document.querySelector("#checkout-button");
      if (!checkoutBtn) {
        // Button not found, do nothing
        return;
      }

      checkoutBtn.addEventListener("click", () => {
        fetch("/payments/create-checkout-session/")
          .then((result) => result.json())
          .then((data) => {
            console.log(data);
            return stripe.redirectToCheckout({ sessionId: data.sessionId });
          })
          .then((res) => {
            console.log(res);
          });
      });
    });
});