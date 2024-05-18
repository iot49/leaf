import { ESPLoader, FlashOptions, LoaderOptions, Transport } from 'esptool-js';

import { api_url } from '../env';

declare let CryptoJS; // CryptoJS is imported in HTML script

// this ought to be trivial, but perhaps not in JS
function arrayBufferToString(buffer) {
  var array = new Uint8Array(buffer);
  var str = '';
  for (var i = 0; i < array.length; i++) {
    str += String.fromCharCode(array[i]);
  }
  return str;
}
const VERBOSE = false;
const espLoaderTerminal = {
  clean() {
    if (VERBOSE) console.log('clean');
  },
  writeLine(data) {
    if (VERBOSE) console.log(data);
  },
  write(data) {
    if (VERBOSE) console.log(data);
  },
};

export async function flash_esp(tag, eraseFlash, chip_callback, progress_callback) {
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
  const transport = new Transport(device, true);

  // connect to device and flash
  let serialOptions = {
    transport,
    baudrate: 921600,
    terminal: espLoaderTerminal,
    debugLogging: false,
    enableTracing: false,
  } as LoaderOptions;
  const esploader = new ESPLoader(serialOptions);

  // verify chip version info
  const chip = await esploader.main();
  const flashSize = await esploader.getFlashSize();
  console.log(`\n${chip} with ${flashSize / 1024} MB flash\n`);
  chip_callback(chip, flashSize);
  if (chip != 'ESP32-S3') {
    console.log(`This is a ${chip}. Leaf is currently only supported on ESP32-S3.`);
    return;
  }

  // download firmware
  console.log('Download firmware', tag);
  const url = `${api_url}/api/vm/${tag}/ESP32_S3_N16R8/firmware.bin`;
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/octet-stream' },
    responseType: 'arraybuffer',
  } as RequestInit);
  const array = await response.arrayBuffer();
  const data = arrayBufferToString(array);

  // write flash
  const fileArray = [
    {
      address: 0,
      data: data,
    },
  ];
  const flashOptions = {
    fileArray: fileArray,
    flashSize: 'keep',
    eraseAll: eraseFlash,
    compress: true,
    reportProgress: progress_callback,
    calculateMD5Hash: (image) => CryptoJS.MD5(CryptoJS.enc.Latin1.parse(image)),
  } as FlashOptions;
  console.log('flashOptions', flashOptions);
  await esploader.writeFlash(flashOptions);
  console.log('Done writing flash');
}
