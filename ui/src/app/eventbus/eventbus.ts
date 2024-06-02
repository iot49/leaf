import { LeafMain } from '../../leaf-main.ts';
import { api_get } from '../api.ts';
import { alertDialog } from '../dialog.ts';
import { BleBus } from './ble-bus.ts';
import { WsBus } from './ws-bus.ts';

export interface Bus {
  readonly connected: boolean;
  disconnect();
  postEvent(event: object): Promise<void>;
}

export interface EventBus extends Bus {
  connect(tree_id: string, bluetooth: boolean): Promise<any>;
}

class _EventBus implements EventBus {
  private ping_interval: number = 5000;
  private _bus: Bus;
  private _wdtId: ReturnType<typeof setInterval>;
  private _connected: boolean = false;

  constructor() {
    // post ping's to server to avoid disconnect
    window.addEventListener('leaf-connection', (event: CustomEvent) => {
      console.log('eventbus.leaf-connection', event.detail);
      // if (this.connected && this._bus.connected) {
      if (this.connected && this._bus.connected) {
        // connected ...
        const pingId = setInterval(() => {
          if (this.connected) {
            this.postEvent({ type: 'ping' });
          } else {
            console.log("disconnected, stop sending ping's");
            clearInterval(pingId);
          }
        }, this.ping_interval);
        // detect disconnect if no communication (e.g. pong) from host
        this._wdtId = setTimeout(this.disconnect.bind(this), this.ping_interval + 10);
      } else {
        // clear the watchdog
        clearInterval(this._wdtId);
      }
    });

    // hello events
    window.addEventListener('leaf-event', async (_event: CustomEvent) => {
      // received message -> reset wdt (equivalent to feeding it)
      clearInterval(this._wdtId);
      // start a new wdt
      if (this._connected) this._wdtId = setTimeout(this.wdt_timeout.bind(this), this.ping_interval + 10);

      const event = _event.detail;
      if (event.type !== 'pong') console.log('EB GOT', event);
      switch (event.type) {
        case 'get_auth':
          try {
            const client_token = await api_get('client_token');
            await this.postEvent({ type: 'put_auth', token: client_token });
          } catch (error) {
            alertDialog('Authentication Failed', error.message);
          }
          break;
        case 'hello_connected':
          // eventbus is operational, start sending ping's
          console.log('connected:', event);
          this._connected = true;
          this.ping_interval = 1000 * event.param.timeout_interval;
          break;
        case 'hello_no_token':
        case 'hello_invalid_token':
          console.log('connection attempt failed:', event);
          this._connected = false;
          await this.disconnect();
          break;
        case 'bye_timeout':
          console.log('server disconnect', event);
          await this.disconnect();
          this._connected = false;
          break;
        default:
          break;
      }
    });
  }

  get connected() {
    return this._connected;
  }

  async connect(tree_id: string, bluetooth: boolean = false) {
    this.disconnect();
    this._bus = bluetooth ? new BleBus(tree_id) : new WsBus(tree_id);
  }

  async disconnect() {
    await this.postEvent({ type: 'bye' });
    this._connected = false;
    if (this._bus) await this._bus.disconnect();
    this._bus = null;
  }

  async postEvent(event: any) {
    if (event.type != 'ping') console.log('EB POST', event);
    if (this.connected) await this._bus.postEvent(event);
  }

  async wdt_timeout() {
    console.log('eventbus.wdt_timeout');
    this.disconnect();
    const main: LeafMain = document.querySelector('leaf-main');
    await main.goto();
  }
}

// global eventbus (singleton)
export const eventbus = new _EventBus();
