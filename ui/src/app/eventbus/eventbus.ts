import { api_get } from '../api.ts';
import { BleBus } from './ble-bus.ts';
import { WsBus } from './ws-bus.ts';

export interface EventBus {
  readonly connected: boolean;
  connect(tree_id: string, bluetooth: boolean): Promise<any>;
  disconnect();
  postEvent(event: object): Promise<any>;
}

export interface Bus {
  readonly connected: boolean;
  disconnect();
  postEvent(event: object): Promise<void>;
}

class _EventBus implements EventBus {
  private ping_interval: number = 5000;
  private _bus: Bus;
  private _wdtId: ReturnType<typeof setInterval>;

  constructor() {
    // post ping's to server to avoid disconnect
    window.addEventListener('leaf-connection', (_) => {
      if (this.connected) {
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
        this._wdtId = setTimeout(this.disconnect.bind(this), 2 * this.ping_interval);
      } else {
        // clear the watchdog
        clearInterval(this._wdtId);
      }
    });

    // hello events
    window.addEventListener('leaf-event', async (_event: CustomEvent) => {
      // recieved message -> reset wdt (equivalent to feeding it)
      clearInterval(this._wdtId);
      // start a new wdt
      this._wdtId = setTimeout(this.wdt_timeout.bind(this), 2 * this.ping_interval);

      const event = _event.detail;
      // if (event.type !== 'pong') console.log('eventbus: leaf-event', event);
      switch (event.type) {
        case 'get_auth':
          const client_token = await api_get('client_token');
          await this.postEvent({ type: 'post_auth', token: client_token });
          break;
        case 'hello_connected':
          this.ping_interval = 1000 * event.param.timeout_interval;
          break;
        default:
          break;
      }
    });
  }

  get connected() {
    return this._bus.connected;
  }

  async connect(tree_id: string, bluetooth: boolean = false) {
    this.disconnect();
    this._bus = bluetooth ? new BleBus(tree_id) : new WsBus(tree_id);
  }

  async disconnect() {
    if (this._bus) this._bus.disconnect();
  }

  async postEvent(event: any) {
    if (event.type != 'ping') console.log('eventbus.postEvent', event);
    return this._bus.postEvent(event);
  }

  async wdt_timeout() {
    console.log('eventbus.wdt_timeout');
    this.disconnect();
  }
}

// global eventbus
export const eventbus = new _EventBus();
