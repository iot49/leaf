import { ContextProvider } from '@lit/context';
import { customElement } from 'lit/decorators.js';
import { LeafBase } from './leaf-base';

import { api_get } from './app/api';
import { Config, configContext, Connected, connectedContext, logContext, settingsContext, stateContext } from './app/context/contexts';
import { SettingsCache } from './app/context/settings-cache';
import { eventbus } from './app/eventbus/eventbus';
import { state_handler } from './app/eventbus/state';

@customElement('leaf-context')
export class LeafContext extends LeafBase {
  public connected: Connected = false;

  public config: Config;
  public settings: any;
  protected settings_cache: SettingsCache;

  private _connectedProvider = new ContextProvider(this, {
    context: connectedContext,
    initialValue: this.connected,
  });
  private _stateProvider = new ContextProvider(this, {
    context: stateContext,
    initialValue: new Map<string, object>(),
  });
  private _configProvider = new ContextProvider(this, {
    context: configContext,
    initialValue: undefined,
  });
  private _logProvider = new ContextProvider(this, {
    context: logContext,
    initialValue: [],
  });
  private _settingsProvider = new ContextProvider(this, {
    context: settingsContext,
    initialValue: undefined,
  });

  constructor() {
    super();

    window.addEventListener('leaf-connection', (event: CustomEvent) => {
      this.connected = event.detail;
      this._connectedProvider.setValue(this.connected, true);
    });

    window.addEventListener('leaf-event', async (_event: CustomEvent) => {
      const event = _event.detail;
      if (event.type != 'pong') console.log('leaf-context got event', event);
      switch (event.type) {
        case 'hello_connected':
          await eventbus.postEvent({ type: 'get_config', dst: '#server' });
          await eventbus.postEvent({ type: 'get_state', dst: '#server' });
          await eventbus.postEvent({ type: 'get_log', dst: '#server' });
          break;

        case 'put_config':
          this.patch_config();
          this.config = event.data;
          this._configProvider.setValue(this.config, true);
          globalThis.leaf.config = this.config;
          break;

        case 'state':
          // state update message
          const proxy = new Proxy(event, state_handler);
          const state = this._stateProvider.value;
          //this.state.set(event.eid, proxy);
          //this._stateProvider.setValue(this.state, true);
          state.set(event.eid, proxy);
          this._stateProvider.setValue(state, true);
          break;

        case 'log':
          // new log message
          this._logProvider.setValue([...this._logProvider.value, event]);
          break;
      }
    });
  }

  private patch_config() {
    // cfg.views[0].cards[0].entities[0].icon = "plus";
    // cfg.views[0].cards[0].entities[2].unit = '%';
    // cfg.views[0].cards[0].entities[2].format = '.1f';
  }

  async connectedCallback(): Promise<void> {
    super.connectedCallback();
    this.settings_cache = new SettingsCache(this._settingsProvider);
    await this.settings_cache.load().then(() => {
      this.settings = this.settings_cache.settings;
      this.requestUpdate();
    });

    // fetch most recent "api/me"
    const me = await api_get('me');
    console.log('me', me);
    if (me) this.settings_cache.settings.me = me;
  }
}
