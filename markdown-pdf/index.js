// index.js
const express = require("express");
const bodyParser = require("body-parser");
const { exec } = require("child_process");
const { spawn, spawnSync } = require("child_process");
// Add this line at the top of your index.js file
const fs = require("fs");
const mongoose = require("mongoose");
const cors = require("cors"); // Import the cors middleware
const PdfModel = require("./models");
const { get } = require("http");
require("dotenv").config();
const { mdToPdf } = require("md-to-pdf");

const app = express();
const port = process.env.PORT || 3001;
const mongoUrl =
  process.env.MONGO_URI ||
  "mongodb+srv://manan:manan123456@cluster0.koatdtt.mongodb.net/?retryWrites=true&w=majority";

var originsWhitelist = ["http://localhost:3000"];
const corsOptions = {
  origin: function (origin, callback) {
    var isWhitelisted = originsWhitelist.indexOf(origin) !== -1 || !origin;
    callback(null, isWhitelisted);
  },
  credentials: true,
  allowedHeaders: [
    "Content-Type",
    "Authorization",
    "X-Requested-With",
    "device-remember-token",
    "Access-Control-Allow-Origin",
    "Origin",
    "Accept",
  ],
  methods: "GET,HEAD,PUT,PATCH,POST,DELETE",
  optionsSuccessStatus: 204,
};
app.use(cors(corsOptions));
app.use(bodyParser.json());
app.use(
  express.urlencoded({
    extended: false,
  })
);

mongoose
  .connect(mongoUrl, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  })
  .then(() => console.log("connected successfully"))
  .catch((err) => console.log("it has an error", err));

// Endpoint to handle the POST request
// Endpoint to handle the POST request

app.get("/", (req, res) => {
  res.send("Hello World!");
});

app.post("/getpdf", async (req, res) => {
  const { markdownContent, slideNum } = req.body;

  const newMdFilePath = `${slideNum}.md`;
  const newPdfFilePath = `${slideNum}.pdf`;
  await mdToPdf({ content: markdownContent }, { dest: newPdfFilePath });
  const savePdf = PdfModel({
    name: slideNum,
    pdf: {
      data: fs.readFileSync(newPdfFilePath),
      contentType: "application/pdf",
    },
  });
  await savePdf.save();

  console.log("Pdf is saved");
  res.send(savePdf);

  // savePdf
  //   .save()
  //   .then(() => {
  //     console.log("Pdf is saved");
  //     res.send(savePdf);
  //     // res.send("Pdf is saved");
  //   })
  //   .catch((err) => {
  //     console.error("Error saving PDF:", err);
  //     res.status(500).json({ error: "Error saving PDF" });
  //   });
  // Write markdown content to a new .md file
  // fs.writeFile(newMdFilePath, markdownContent, (err) => {
  //   if (err) {
  //     console.error("Error writing Markdown file:", err);
  //     return res.status(500).json({ error: "Error writing Markdown file" });
  //   }

  //   const nodePath = "node"; // replace with the actual path from 'which node'

  //   // Use spawnSync
  //   const marpProcess = spawnSync(nodePath, [
  //     "node_modules/.bin/marp",
  //     newMdFilePath,
  //     "-o",
  //     newPdfFilePath,
  //   ]);

  //   if (marpProcess.error) {
  //     console.error("Error running Marp process:", marpProcess.error);
  //     return res.status(500).json({ error: "Error running Marp process" });
  //   }

  //   if (marpProcess.status === 0) {
  //     // Marp process executed successfully
  //     const savePdf = PdfModel({
  //       name: slideNum,
  //       pdf: {
  //         data: fs.readFileSync(newPdfFilePath),
  //         contentType: "application/pdf",
  //       },
  //     });

  //     savePdf
  //       .save()
  //       .then(() => {
  //         console.log("Pdf is saved");
  //         res.send(savePdf);
  //         // res.send("Pdf is saved");
  //       })
  //       .catch((err) => {
  //         console.error("Error saving PDF:", err);
  //         res.status(500).json({ error: "Error saving PDF" });
  //       });
  //   } else {
  //     console.error("Marp process failed with code:", marpProcess.status);
  //     res.status(500).json({ error: "Marp process failed" });
  //   }
  // });
});

const getpdf = async (slideNum) => {
  const filteredData = await PdfModel.findOne({ name: slideNum });
  console.log("filteredData", filteredData);
  return filteredData;
};

app.post("/getOnePdf", async (req, res) => {
  const { slideNum } = req.body;
  const filteredData = await PdfModel.findOne({ name: slideNum });
  // console.log("filteredData", filteredData.pdf.data);
  res.send(filteredData);
});

app.get("/getpdf", async (req, res) => {
  const filteredData = await PdfModel.find();
  console.log("filteredData all", filteredData);
  res.send(filteredData);
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});

module.exports = app;
