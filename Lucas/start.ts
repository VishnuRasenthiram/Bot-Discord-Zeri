import waifu2x from "waifu2x";

async function upscaleImage() {
  try {
    let progress = (current: number, total: number) => {
      console.log(`Current Image: ${current} Total Images: ${total}`)
      if (current === total) return true
    }
    setTimeout(() => {
      
    }, 1000);
    await waifu2x.upscaleImages(
      "C:/Users/theob/Downloads/Webtoon-Downloader-master (1)/Webtoon-Downloader-master/src/Lecteur_omniscient",
      "C:/Users/theob/Downloads/Webtoon-Downloader-master (1)/Webtoon-Downloader-master/src/upscaled",
      {
        noise: 1,
        rename: '_BIS',
       // jpgWebpQuality:3,
        //jpgWebpQuality: 10,
       //pngCompression: 5,
       //parallelFrames: 5,
        //limit: 10,
        upscaler: "real-esrgan",
      //  threads: 4,
       // blockSize:64,
        scale: 2
      }, progress);
    console.log("Image upscale complete");
  } catch (error) {
    console.error("Error upscaling image:", error);
  }
}

upscaleImage();
