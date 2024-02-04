const mongoose = require("mongoose");

const pdfSchema = new mongoose.Schema({
  name: String,
  pdf: {
    data: Buffer,
    contentType: String,
  },
});

module.exports = PdfModel = mongoose.model("Pdf", pdfSchema);
