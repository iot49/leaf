import { alertDialog } from '../dialog';
import { ws_url } from '../env';
import { Bus } from './eventbus';

const CONNECTION_RETRY_MS = 5000;

export class WsBus implements Bus {
  public tree_id: string;
  private _ws: WebSocket;
  private _reconnect: boolean = true; // reconnect unless explicitly disconnected
  private _connected: boolean = false;

  constructor(tree_id: string) {
    this.tree_id = tree_id;
    this.connect();
  }

  /**
   * Indicates whether the WebSocket connection is currently open.
   * Note: this does not necessarily mean that the eventbus has been authenticated & is operational.
   *
   * this._ws.readyState === this._ws.OPEN appears to be unreliable.
   * Instead we rely on status events and disonnect().
   */
  public get connected(): boolean {
    return this._connected; // && (this._ws ? this._ws.readyState === this._ws.OPEN : false);
  }

  public async postEvent(event: any) {
    try {
      if (this.connected) this._ws.send(JSON.stringify(event));
    } catch {
      alertDialog('WsBus', `ws-bus.send failed for ${JSON.stringify(event, null, 2)}`);
      console.log('ws-bus.postEvent - failed to send event', event);
    }
  }

  /**
   * Attempts connection to server.
   * Automatically reconnects if connection is lost. To stop reconnecting, call disconnect().
   */
  protected connect() {
    this._ws = new WebSocket(this._url);

    // connect, then reconnect when connection is lost
    let timer = setInterval(() => {
      if (this._reconnect && !this.connected) {
        // lost connection or never connected
        this._connected = false;
        clearInterval(timer);
        // disable the old ws
        this._ws.removeEventListener('message', this._message_event);
        try {
          this._ws.close();
        } catch {
          console.log('ws-bus.reconnect - cannot close old ws');
        }
        // create a new websocket
        this.connect();
      }
    }, CONNECTION_RETRY_MS);

    // eventbus
    this._ws.addEventListener('message', this._message_event.bind(this));

    // websocket status events (open, close, error)
    // note: we don't remove these - presumably the garbage collector will take care of it when it collects _ws?
    this._ws.addEventListener('open', (_) => {
      this._connected = true;
      this._notify_connection(true);
    });
    this._ws.addEventListener('close', (_) => {
      // looks like the server closed the connection
      this._connected = false;
      this._notify_connection(false);
    });
    this._ws.addEventListener('error', (event) => {
      // hmm, what went wrong?
      this._connected = false;
      this._notify_connection(false);
      try {
        console.error('ws-bus.ws.error - closing ws', event);
        this._ws.close();
      } catch {
        console.log('ws-bus.status_event - failed to close ws');
        // app.overlay = html`<sl-dialog label="WsBus" open>FAILED to close websocket</sl-dialog>`;
      }
    });
  }

  /**
   * Immediately disconnects from server and stops automatic reconnects.
   * Call connect() to reconnect.
   * Note: if the eventbus is operational, send a 'bye' event before calling disconnect().
   */
  public disconnect() {
    this._connected = false;
    this._reconnect = false;
    if (this.connected) this._ws.close();
    // immediately notify of disconnect as the actual close of the ws takes some time
    this._notify_connection(false);
  }

  protected get _url() {
    return `${ws_url}/ws`;
  }

  private _notify_connection(connected: boolean) {
    window.dispatchEvent(
      new CustomEvent('leaf-connection', {
        bubbles: true,
        composed: true,
        detail: connected,
      })
    );
  }

  private _message_event(event) {
    window.dispatchEvent(
      new CustomEvent('leaf-event', {
        bubbles: true,
        composed: true,
        detail: JSON.parse(event.data),
      })
    );
  }
}
