import { ESPLoader, FlashOptions, LoaderOptions, Transport } from 'esptool-js';

import { CryptoJS } from 'crypto-js';

export async function flash_esp(url, progress_callback) {
  // connect to device
  const portFilters = [
    {
      // esp32s3 wroom module (boot mode)
      usbVendorId: 0x303a,
      usbProductId: 0x1001,
    },
  ];
  const device = await (navigator as Navigator & { serial?: any }).serial?.requestPort({
    filters: portFilters,
  });
  console.log('device', device);
  const transport = new Transport(device, true);

  // create a terminal
  const espLoaderTerminal = {
    clean() {
      //console.log('------------------------- clean');
    },
    writeLine(data) {
      //console.log(data);
    },
    write(data) {
      //console.log(data);
    },
  };

  // connect to device and flash
  try {
    let serialOptions = {
      transport,
      baudrate: 921600,
      terminal: espLoaderTerminal,
    } as LoaderOptions;
    const esploader = new ESPLoader(serialOptions);

    // verify chip version info
    const chip = await esploader.main();
    const flashSize = await esploader.getFlashSize();
    console.log(`\n${chip} with ${flashSize / 1024} MB flash\n`);
    //term.writeln(`Flash size: ${flashSize / 1024} MB`);
    if (chip != 'ESP32-S3') {
      console.log(`This is a ${chip}. Leaf is currently only supported on ESP32-S3.`);
      return;
    }

    // write flash
    console.log('Writing flash...');
    const response = await fetch(url, {
      method: 'GET',
      headers: { 'Access-Control-Allow-Origin': 'http://localhost:5173', 'Content-Type': 'application/octet-stream' },
    });
    const binary = await response.blob();
    console.log('binary', binary.size, binary);
    const fileArray = [
      {
        address: 0,
        data: '',
      },
    ];
    const flashOptions = {
      fileArray: fileArray,
      flashSize: 'keep',
      eraseAll: this.eraseFlash,
      compress: true,
      reportProgress: progress_callback,
      calculateMD5Hash: (image) => CryptoJS.MD5(CryptoJS.enc.Latin1.parse(image)),
    } as FlashOptions;
    await esploader.writeFlash(flashOptions);
  } catch (e) {
    console.log(`Error: ${e.message}`);
    return;
  }
}
