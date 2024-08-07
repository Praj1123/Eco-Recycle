const express = require('express');
const app = express();
const port = 3000;
const bodyparser = require("body-parser");
const Razorpay = require('razorpay');
app.use(bodyparser.json());
var instance = new Razorpay({
  key_id: 'rzp_test_Rtep49rO7VTb44',
  key_secret: 'Nb3IX0LuwKbjoOv7fRvmzB7k',
});

app.get('/', (req, res) => {
  res.sendFile("details.html", { root: __dirname });
})

app.post('/create/orderId', (req, res) => {
  console.log("create orderId request", req.body);
  var options = {
    amount: req.body.amount * 100, // amount in the smallest currency unit
    currency: "INR",
    receipt: "order_rcptid_11"
  };
  instance.orders.create(options, (err, order) => {
    console.log(order);
    res.send({ orderId: order.id })
  })
})

app.post("/api/payment/verify", (req, res) => {
  const { razorpay_order_id, razorpay_payment_id, razorpay_signature } = req.body;
  const body = razorpay_order_id + "|" + razorpay_payment_id;
  const expectedSignature = instance.signatures.verify(body, razorpay_signature);
  console.log(expectedSignature);
  res.json({ signatureIsValid: expectedSignature });
});

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`)
})