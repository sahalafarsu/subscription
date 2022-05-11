var stripe = Stripe('pk_test_51KtS69SGpZ0PrA5CW0flAi8ScqqnYaQhgN3sZGmrO0aqaL0ENXl3wq6iNGlqkg3knJWCnZzNtw378PvXoB0Hro9z0039uxC98h');

var checkoutButton = document.getElementById('checkout-button');

checkoutButton.addEventListener('click', function() {
  stripe.redirectToCheckout({
    // Make the id field from the Checkout Session creation API response
    // available to this file, so you can provide it as argument here
    // instead of the {{CHECKOUT_SESSION_ID}} placeholder.
    sessionId: sessionid
  }).then(function (result) {
    // If `redirectToCheckout` fails due to a browser or network
    // error, display the localized error message to your customer
    // using `result.error.message`.
  });
});