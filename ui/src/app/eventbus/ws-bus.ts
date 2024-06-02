import { ws_url } from '../env';
import { EventEmitter, IEventEmitter } from '../event-emitter';
import { Transport } from './eventbus';

export class WsBus extends EventEmitter implements IEventEmitter, Transport {
  private _ws: WebSocket;
  private _connected: boolean = false;

  constructor(_treeId: string) {
    super();
    const url = `${ws_url}/ws`; // TODO: url based on treeId
    this._ws = new WebSocket(url);

    // eventbus
    this._ws.addEventListener('message', (event: MessageEvent) => {
      // Update the type of 'event' to be 'MessageEvent'
      this.emit('message', event.data);
    });

    // websocket status events (open, close, error)
    this._ws.addEventListener('open', (_) => {
      this._connected = true;
      this.emit('connected');
    });

    this._ws.addEventListener('close', (event: CloseEvent) => {
      // looks like the server closed the connection
      this._connected = false;
      this.emit('disconnected', `server closed connection: ${event.reason}`);
    });

    this._ws.addEventListener('error', (event) => {
      // hmm, what went wrong?
      this._connected = false;
      this.emit('disconnected', event);
    });
  }
  /**
   * Indicates whether the WebSocket connection is currently open.
   * Note: this does not necessarily mean that the eventbus has been authenticated & is operational.
   */
  public get connected(): boolean {
    return this._connected;
  }

  public async send(msg: any) {
    if (this.connected) this._ws.send(msg);
  }

  public disconnect(msg: string = '') {
    if (this.connected) this._ws.close();
    this._connected = false;
    this.emit('disconnected', msg);
    this.clear();
  }
}
