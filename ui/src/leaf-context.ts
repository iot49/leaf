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

    eventbus.on('#connected', async () => {
      console.log('LeafContext: #connected');
      this.connected = true;
      this._connectedProvider.setValue(this.connected, true);
      await eventbus.postEvent({ type: 'get_config', dst: '#server' });
      await eventbus.postEvent({ type: 'get_state', dst: '#server' });
      // await eventbus.postEvent({ type: 'get_log', dst: '#server' });
    });

    eventbus.on('#disconnected', (msg) => {
      console.log('LeafContext: disconnected', msg);
      this.connected = false;
      this._connectedProvider.setValue(this.connected, true);
    });

    eventbus.on('state', (event) => {
      // state update message
      // console.log('state update, notifying context', event);
      const proxy = new Proxy(event, state_handler);
      const state = this._stateProvider.value;
      state.set(event.eid, proxy);
      this._stateProvider.setValue(state, true);
    });

    eventbus.on('put_config', (event) => {
      this.config = event.data;
      this._configProvider.setValue(this.config, true);
      globalThis.leaf.config = this.config;
      this.requestUpdate();
    });

    eventbus.on('log', (event) => {
      this._logProvider.setValue([...this._logProvider.value, event]);
    });
  }

  async connectedCallback(): Promise<void> {
    super.connectedCallback();
    this.settings_cache = new SettingsCache(this._settingsProvider);
    await this.settings_cache
      .load()
      .then(() => {
        this.settings = this.settings_cache.settings;
        globalThis.leaf.settings = this.settings;
        this.requestUpdate();
      })
      .catch((error) => {
        console.log('error fetching settings_cache', error);
      });

    // fetch most recent "api/me"
    const me = await api_get('me');
    console.log('me', me);
    if (me) this.settings_cache.settings.me = me;
  }
}
