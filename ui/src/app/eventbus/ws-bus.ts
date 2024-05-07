import { alertDialog } from '../dialog';
import { Bus } from './eventbus';

export class WsBus implements Bus {
  public tree_id: string;
  private _ws: WebSocket;
  private _reconnect: boolean = true; // reconnected unless explicitly disconnected

  constructor(tree_id: string) {
    this.tree_id = tree_id;
    this.connect();
  }

  public async postEvent(event: any) {
    try {
      this._ws.send(JSON.stringify(event));
    } catch {
      alertDialog('WsBus', `ws-bus.send failed for ${event}`);
      console.log('ws-bus.postEvent - failed to send event');
    }
  }

  public disconnect() {
    console.log('ws-bus.disconnect');
    this._reconnect = false;
    if (this.connected) this._ws.close();
    // immediately notify of disconnect as the actual close of the ws takes some time
    window.dispatchEvent(
      new CustomEvent('leaf-connection', {
        bubbles: true,
        composed: true,
        detail: false,
      })
    );
  }

  public get connected(): boolean {
    return this._ws ? this._ws.readyState === this._ws.OPEN : false;
  }

  protected connect() {
    this._ws = new WebSocket(this._url());

    // connect, then reconnect when connection is lost
    let timer = setInterval(() => {
      if (this._reconnect && !this.connected) {
        // lost connection or never connected
        clearInterval(timer);
        // disable the old ws
        this._ws.removeEventListener('message', this.message_event);
        try {
          this._ws.close();
        } catch {
          console.log('ws-bus.reconnect - cannot close old ws');
        }
        // create a new websocket
        this.connect();
      }
    }, 5000);

    // eventbus
    this._ws.addEventListener('message', this.message_event.bind(this));

    // websocket status events (open, close, error)
    const handler = this.status_event.bind(this);
    this._ws.addEventListener('open', handler);
    this._ws.addEventListener('close', handler);
    this._ws.addEventListener('onerror', handler);
  }

  protected _url() {
    if (this.tree_id === '#earth') {
      // return `ws://localhost:8001/ws`;
      return `wss://${location.host}/ws`;
      // return `wss://leaf49.org/ws`;
    }
    console.log('NOT IMPLEMENTED: local connection to tree', this.tree_id);
  }

  private message_event(event) {
    window.dispatchEvent(
      new CustomEvent('leaf-event', {
        bubbles: true,
        composed: true,
        detail: JSON.parse(event.data),
      })
    );
  }

  private status_event(event) {
    // websocket status events (open, close, error)
    const state = event.target.readyState;
    if (state !== WebSocket.CONNECTING && state !== WebSocket.OPEN) {
      try {
        console.log('ws-bus.status_event - closing ws');
        event.target.close();
      } catch {
        console.log('ws-bus.status_event - failed to close ws');
        // app.overlay = html`<sl-dialog label="WsBus" open>FAILED to close websocket</sl-dialog>`;
      }
    }
    window.dispatchEvent(
      new CustomEvent('leaf-connection', {
        bubbles: true,
        composed: true,
        detail: this.connected,
      })
    );
  }
}
