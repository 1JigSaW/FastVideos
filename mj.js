const { Midjourney } = require("midjourney");
const sharp = require("sharp");
const fs = require("fs");
const path = require("path");
require("dotenv").config();

const query = process.argv[2];
const VAR = process.argv[3];

const clientMidjourney = new Midjourney({
  ServerId: process.env.SERVER_ID,
  ChannelId: process.env.CHANNEL_ID,
  SalaiToken: process.env.SALAI_TOKEN,
});

async function main() {
  await clientMidjourney.Connect();
  let newQuery = query + " --ar 9:19 --no text fonts letters watermark words typography slogans signature";
  const result = await clientMidjourney.Imagine(newQuery, (uri, progress) => {
    console.log("Imagine", uri, "progress", progress);
  });

  const { id, hash, flags, uri: imagineUri } = result;

  const responseImagine = await fetch(imagineUri);
  const arrayBuffer = await responseImagine.arrayBuffer();
  const bufferImagine = Buffer.from(arrayBuffer);

  let metadata;
  try {
    metadata = await sharp(bufferImagine).metadata();
  } catch (error) {
    console.error("Error getting metadata from image:", error);
    throw new Error("Error getting metadata from image");
  }
  const width = metadata.width / 2;
  const height = metadata.height / 2;

  const currentDate = new Date();
  const formattedDate = `${currentDate.getFullYear()}-${currentDate.getMonth() + 1}-${currentDate.getDate()}_${currentDate.getHours()}-${currentDate.getMinutes()}-${currentDate.getSeconds()}`;
  const dirName = `background/${VAR}_${formattedDate}`;

  if (!fs.existsSync(dirName)) {
    fs.mkdirSync(dirName, { recursive: true });
  }

  for (let i = 0; i < 2; i++) {
    for (let j = 0; j < 2; j++) {
      let imageBuffer;
      try {
        imageBuffer = await sharp(bufferImagine)
          .extract({ left: i * width, top: j * height, width, height })
          .jpeg({ quality: 80 })
          .toBuffer();

      } catch (error) {
        console.error("Error processing image:", error);
        throw new Error("Error processing image");
      }

      const fileName = `${i}_${j}_${formattedDate}.jpg`;
      const filePath = path.join(dirName, fileName);

      fs.writeFileSync(filePath, imageBuffer);
      console.log(`Image saved to ${filePath}`);
    }
  }
  process.exit(0); // Explicitly end the process
}

main().catch(error => {
  console.error(error);
  process.exit(1); // Exit with an error status
});
