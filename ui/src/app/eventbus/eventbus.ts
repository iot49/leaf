import { LeafMain } from '../../leaf-main.ts';
import { api_get } from '../api.ts';
import { alertDialog } from '../dialog.ts';
import { EventEmitter, IEventEmitter } from '../event-emitter';
import { BleBus } from './ble-bus.ts';
import { WsBus } from './ws-bus.ts';

/** Event data over some medium, e.g. websockets or bluetooth.
 *
 *  Emits the following events:
 *    connected, disconnected(msg)
 *    msg(data: string)
 */
export interface Transport extends IEventEmitter {
  readonly connected: boolean;
  disconnect();
  send(msg: string): Promise<void>;
}

/**
 * Eventbus is a singleton that connects to the server via WebSockets or Bluetooth.
 * Emits the following events:
 *   #connected, #disconnected(msg)
 *   event topic (e.g. config!, state.update!)
 */
export interface EventBus extends IEventEmitter {
  /** Connection status. */
  readonly connected: boolean;

  /**
   * Connects to server. Automatically reconnects if connection is lost until disconnect() is called.
   * @param tree_id - The ID of the tree to connect to. Defaults to earth.
   * @param bluetooth - A flag indicating whether to use Bluetooth for the connection.
   * @returns A promise that resolves when the server has been contacted (but not yet responded).
   */
  connect(tree_id: string, bluetooth: boolean): Promise<any>;

  /**
   * Disconnects from the current tree (and stops automatic reconnection).
   * @returns A promise that resolves when the disconnection is complete.
   */
  disconnect(): Promise<any>;

  /**
   * Sends event to server.
   * @param event - The event to be posted.
   * @returns A promise that resolves when the event has been posted.
   */
  postEvent(event: any): Promise<void>;
}

class _EventBus extends EventEmitter implements EventBus {
  private ping_interval: number = 5000;
  private _bus: Transport;
  private _connected: boolean = false;
  private _reconnect: boolean = true;

  /**
   * Connected to and authenticated with server.
   * @returns {boolean} The connection status.
   */
  get connected() {
    return this._connected;
  }

  async postEvent(event: any): Promise<void> {
    try {
      this._bus.send(JSON.stringify(event));
    } catch {
      //alertDialog('EventBus', `postEvent failed for ${JSON.stringify(event, null, 2)}`);
      console.log('EventBus', `postEvent failed for ${JSON.stringify(event, null, 2)}`);
    }
  }

  async disconnect() {
    await this.postEvent({ type: 'bye' });
    this._connected = this._reconnect = false;
    if (this._bus) {
      this._bus.clear();
      await this._bus.disconnect();
    }
    this._bus = null;
  }

  async connect(treeId: string, bluetooth: boolean = false) {
    if (this._bus) return;

    // start new connection
    this._bus = bluetooth ? new BleBus(treeId) : new WsBus(treeId);
    const bus = this._bus;
    this._reconnect = true;

    // subscribe to communication events
    bus.on('connected', () => {
      // console.log('transport is connected - nice to know, but wait for handshake from server');
    });

    bus.on('disconnected', 'error', async (msg: string) => {
      console.log('disconnected', msg);
      this._connected = false;
      if (this._reconnect) {
        const delay = (ms) => new Promise((res) => setTimeout(res, ms));
        await delay(5000);
        console.log('reconnect');
        this.connect(treeId, bluetooth);
      }
    });

    bus.on('message', async (data: string) => {
      const event = JSON.parse(data);
      this.emit(event.type, event);
    });

    this.on('get_auth', async () => {
      let client_token;
      try {
        client_token = await api_get('client_token');
      } catch (error) {
        alertDialog('Authentication - could not get token from server', error.message);
        return;
      }
      try {
        await this.postEvent({ type: 'put_auth', token: client_token });
      } catch (error) {
        alertDialog('Authentication - failed sending token to server', error.message);
      }
    });

    this.on('hello_connected', (event) => {
      this.ping_interval = 1000 * event.param.timeout_interval;
      this.pingTask();
      this.wdtTask();
      this._connected = true;
      this.emit('#connected');
    });

    this.on('hello_no_token', 'hello_invalid_token', 'bye_timeout', async (event) => {
      console.log('connection attempt failed:', event);
      this._connected = false;
      this._bus.clear();
      await this.disconnect();
      this._reconnect = true;
      this.connect(treeId, bluetooth);
    });

    this.on('bye', async () => {
      this._connected = false;
      this._reconnect = false;
      this.emit('#disconnected');
    });
  }

  private pingTask() {
    // post ping's to server to avoid disconnect
    const pingId = setInterval(async () => {
      if (this.connected) {
        await this.postEvent({ type: 'ping' });
      } else {
        clearInterval(pingId);
      }
    }, this.ping_interval);
  }

  private wdtTask() {
    const wdt = () => {
      return setTimeout(async () => {
        console.log('eventbus Watchdog timeout (no messages from server)');
        this.disconnect();
        const main: LeafMain = document.querySelector('leaf-main');
        await main.goto();
      }, this.ping_interval + 10);
    };

    // start the watchdog
    let wdtId = wdt();

    this._bus.on('message', (_) => {
      // got a message - reset watchdog timer
      if (wdtId) clearTimeout(wdtId);
      wdtId = wdt();
    });
  }
}

// global eventbus (singleton)
export const eventbus = new _EventBus();
