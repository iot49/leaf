import { css, html } from "lit";
import { customElement, query } from "lit/decorators.js";
import { LeafBase } from "./leaf-base";

import { MpExec } from "./app/mpexec/mpexec";

@customElement("leaf-exec")
export class LeafExec extends LeafBase {
  static styles = [
    css`
      table {
        border-spacing: 20px;
      }
      sl-textarea {
        width: 14cm;
      }
    `,
    super.styles[0],
  ];

  private port;
  private read_buffer = "";
  private mpexec: MpExec;

  @query("#code") code;
  @query("#output") output;
  @query("#error") error;

  async connect() {
    this.mpexec = new MpExec();
    await this.mpexec.openDevice("s3", false);
  }

  inWaiting() {
    return this.read_buffer.length;
  }

  async read(n = -1) {
    if (n === -1) n = this.read_buffer.length;
    while (this.read_buffer.length < n) {
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
    const data = this.read_buffer.slice(0, n);
    this.read_buffer = this.read_buffer.slice(n);
    return data;
  }

  async write(data) {
    const encoder = new TextEncoder();
    const dataArrayBuffer = encoder.encode(data);
    if (this.port && this.port.writable) {
      const writer = this.port.writable.getWriter();
      await writer.write(dataArrayBuffer);
      writer.releaseLock();
    }
  }

  render() {
    return html`
      <link
        href="https://cdn.jsdelivr.net/npm/xterm@4.19.0/css/xterm.css"
        rel="stylesheet" />

      <leaf-page>
        <nav slot="nav">Exec</nav>
        <main>
          <sl-button
            variant="primary"
            @click=${async (_) => await this.connect()}
            >Connect</sl-button
          >
          <sl-textarea
            id="code"
            label="Code"
            help-text="MicroPython Code"></sl-textarea>
          <sl-button
            @click=${async (_) => {
              if (!this.mpexec || !this.mpexec.connected()) {
                console.error("Not connected");
                return;
              }
              const [res, err] = await this.mpexec.exec(this.code.value);
              this.output.value = res;
              this.error.value = err;
            }}
            >Exec</sl-button
          >
          <sl-textarea id="output" label="Output"></sl-textarea>
          <sl-textarea id="error" label="Error"></sl-textarea>
          <sl-button @click=${async (_) => await this.mpexec.close()}
            >Close</sl-button
          >
        </main>
      </leaf-page>
    `;
  }
}
