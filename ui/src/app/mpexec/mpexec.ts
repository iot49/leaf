import { SerialTransport } from './transport_serial.js';

export class Port {
  private port: SerialPort;
  private read_buffer: Uint8Array = new Uint8Array();

  constructor(port) {
    this.port = port;
    // buffer incoming data
    const This = this; // backdoor to this in callback
    const appendStream = new WritableStream({
      write(chunk: Uint8Array) {
        This.read_buffer = new Uint8Array([...This.read_buffer, ...chunk]);
      },
    });
    this.port.readable.pipeTo(appendStream);
  }

  connected() {
    return this.port && this.port.readable;
  }

  inWaiting(): number {
    return this.read_buffer.length;
  }

  async write(data: string) {
    const encoder = new TextEncoder();
    const dataArrayBuffer = encoder.encode(data);
    if (this.port && this.port.writable) {
      const writer = this.port.writable.getWriter();
      try {
        await writer.write(dataArrayBuffer);
      } finally {
        writer.releaseLock();
      }
    }
  }

  async readUint8(n = -1): Promise<Uint8Array> {
    if (n < 0) {
      const res = this.read_buffer;
      this.read_buffer = new Uint8Array();
      return res;
    }
    while (this.read_buffer.length < n) {
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
    const data = this.read_buffer.slice(0, n);
    this.read_buffer = this.read_buffer.slice(n);
    return data;
  }

  async readUint16(n = -1): Promise<Uint16Array> {
    const uint8Array = await this.readUint8(n * 2);
    return new Uint16Array(uint8Array.buffer);
  }

  async read(n = -1): Promise<string> {
    const uint8Array = await this.readUint8(n);
    const decoder = new TextDecoder();
    return decoder.decode(uint8Array);
  }
}

export class MpExec extends SerialTransport {
  serial: Port;

  static portFilters = {
    s3: [[{ usbProductId: 4097, usbVendorId: 12346 }], [{ usbProductId: 32980, usbVendorId: 12346 }]],
  };

  async openDevice(device = 's3', bootloader = false, baudRate = 115200) {
    const portFilter = MpExec.portFilters[device][bootloader ? 0 : 1];
    console.log('mpexec.portFilter', portFilter);
    const port = await (navigator as Navigator & { serial?: any }).serial?.requestPort({
      filters: portFilter,
    });
    await port.open({ baudRate: baudRate });
    console.log('mpexec.open port', port.getInfo());
    this.serial = new Port(port);
  }

  async openPort(port) {
    this.serial = new Port(port);
  }

  async exec(code, soft_reset = false) {
    /* 
      Execute code on the MicroPython device using raw REPL if available.
    
      Example:
        const mpexec = new MpExec();
        await mpexec.openDevice("s3");
        const [res, err] = await mpexec.exec("print('hello')");
        console.log(res, err);
      */
    await super.enter_raw_repl(soft_reset);
    return await super.exec_raw(code);
  }

  connected() {
    return this.serial && this.serial.connected();
  }

  async close() {
    // closing webserial ports is exceedingly difficult
    // this does the trick, but throws
    //      Uncaught (in promise) DOMException: The device has been lost.
    // How catch the exception? This seems to sort of work:
    // neither message below appars in log, but another error is reported
    this.exec('import machine; machine.reset()')
      .then(() => console.log('successfully closed port'))
      .catch(() => console.log('ERROR closing port'));
  }
}
