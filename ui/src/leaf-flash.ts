import { css, html, PropertyValueMap } from "lit";
import { customElement, query } from "lit/decorators.js";

import { LeafBase } from "./leaf-base";

//import { Terminal } from "@xterm/xterm";
import { ESPLoader, FlashOptions, LoaderOptions, Transport } from "esptool-js";

declare let Terminal; // Terminal is imported in HTML script
declare let CryptoJS; // CryptoJS is imported in HTML script

@customElement("leaf-flash")
export class LeafFlash extends LeafBase {
  static styles = [
    css`
      table {
        border-spacing: 20px;
      }
    `,
    super.styles[0],
  ];

  eraseFlash = false;

  @query("#terminal") terminal;
  @query("#firmware") firmware;

  protected firstUpdated(
    _changedProperties: PropertyValueMap<any> | Map<PropertyKey, unknown>,
  ): void {
    console.log("LeafFlash.firstUpdated");
  }

  async flash() {
    // connect to device
    const portFilters = [
      {
        // esp32s3 wroom module (boot mode)
        usbVendorId: 0x303a,
        usbProductId: 0x1001,
      },
    ];
    const device = await (
      navigator as Navigator & { serial?: any }
    ).serial?.requestPort({
      filters: portFilters,
    });
    console.log("device", device);
    const transport = new Transport(device, true);

    // create a terminal
    const term = new Terminal({ cols: 120, rows: 40 });
    term.open(this.terminal);
    const espLoaderTerminal = {
      clean() {
        term.clear();
      },
      writeLine(data) {
        term.writeln(data);
      },
      write(data) {
        term.write(data);
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
      term.writeln(`\n${chip} with ${flashSize / 1024} MB flash\n`);
      //term.writeln(`Flash size: ${flashSize / 1024} MB`);
      if (chip != "ESP32-S3") {
        term.writeln(
          `This is a ${chip}. Leaf is currently only supported on ESP32-S3.`,
        );
        return;
      }

      // write flash
      term.writeln("Writing flash...");

      const fileArray = [
        {
          address: 0,
          data: "", // actual binary data to flash, fetch this via https
        },
      ];
      const flashOptions = {
        fileArray: fileArray,
        flashSize: "keep",
        eraseAll: this.eraseFlash,
        compress: true,
        reportProgress: this.reportProgress,
        calculateMD5Hash: (image) =>
          CryptoJS.MD5(CryptoJS.enc.Latin1.parse(image)),
      } as FlashOptions;
      await esploader.writeFlash(flashOptions);
    } catch (e) {
      term.writeln(`Error: ${e.message}`);
      return;
    }
  }

  render() {
    return html`
      <link
        href="https://cdn.jsdelivr.net/npm/xterm@4.19.0/css/xterm.css"
        rel="stylesheet" />

      <leaf-page>
        <nav slot="nav">Flash</nav>
        <main>
          <input type="file" id="firmware" name="myfile" />
          <div id="terminal"></div>
          <sl-button variant="primary" @click=${async (_) => await this.flash()}
            >Flash Now</sl-button
          >
        </main>
      </leaf-page>
    `;
  }

  reportProgress(i, bytesSent, totalBytes) {
    console.log("progress", i, bytesSent, totalBytes);
  }
}
