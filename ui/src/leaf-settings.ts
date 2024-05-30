import { consume } from '@lit/context';
import 'lit';
import { css, html } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { api_get, api_put } from './app/api';
import { Settings, settingsContext } from './app/context/contexts';
import { LeafBase } from './leaf-base';

@customElement('leaf-settings')
export class LeafSettings extends LeafBase {
  static styles = [
    ...LeafBase.styles,
    css`
      main {
        margin: 1rem;
      }
      sl-input::part(base) {
        background-color: transparent;
        border: none;
      }
      sl-input::part(input) {
        padding: 0;
      }
      .disabled sl-input::part(base) {
        text-decoration: line-through;
      }
      .td-item {
        font-weight: bold;
        margin-right: 2rem;
        padding-right: 2rem;
      }
    `,
  ];

  @consume({ context: settingsContext, subscribe: true })
  @property({ attribute: false })
  private settings: Settings;

  @state()
  private users: any = [];

  @state()
  private keys: any = [];

  @state()
  private env: any = {};

  @state()
  private connections: any = {};

  async connectedCallback() {
    super.connectedCallback();
    if (this.settings.me.superuser) {
      this.users = await api_get('user');
      this.keys = await api_get('api_key');
      this.env = await api_get('dev/env');
      window.setInterval(async () => {
        this.connections = await api_get('connections');
      }, 10000);
    }
  }

  meSettingsTemplate() {
    const me = this.settings.me;
    return html`
      <table class="me-settings">
        <tr>
          <td class="td-item" align="right">email</td>
          <td>${me.email}</td>
        </tr>
        <tr>
          <td class="td-item" align="right">name</td>
          <td>
            <sl-input value=${me.name} @sl-change="${async (e) => await api_put(`me`, { name: e.target.value })}"> </sl-input>
          </td>
        </tr>
        <tr>
          <td class="td-item" align="right">member since</td>
          <td><sl-relative-time date="${me.created_at}Z"></sl-relative-time></td>
        </tr>
        <tr>
          <td class="td-item" align="right">auto connect</td>
          <td>
            <sl-switch
              size="medium"
              ?checked=${this.settings.auto_connect}
              @sl-change=${(e) => (this.settings.auto_connect = e.target.checked)}
            ></sl-switch>
          </td>
        </tr>
        <tr>
          <td class="td-item" align="right">dark theme</td>
          <td>
            <sl-switch
              size="medium"
              ?checked=${this.settings.dark_theme}
              @sl-change=${(e) => {
                const dark = e.target.checked;
                this.settings.dark_theme = dark;
                document.querySelector('body').setAttribute('theme', dark ? 'dark' : 'light');
              }}
            ></sl-switch>
          </td>
        </tr>
      </table>
    `;
  }

  usersTemplate() {
    const users = this.users;
    return html` <table class="zebra-table">
      <tr>
        <td>email</td>
        <td>Name</td>
        <td>Superuser</td>
        <td>Role</td>
        <td>Created</td>
        <td>Updated</td>
        <td>Disabled</td>
      </tr>
      ${users.map(
        (user: any) => html`
          <tr class=${user.disabled ? 'disabled' : ''}>
            <td>${user.email}</td>
            <td>${user.name}</td>
            <td align="center">
              <sl-checkbox
                ?checked=${user.superuser}
                @sl-change=${async (e) => {
                  await api_put(`user/${user.uuid}`, { superuser: e.target.checked });
                  this.users = await api_get('user');
                }}
              ></sl-checkbox>
            </td>
            <td>
              <sl-radio-group
                value=${user.roles[0]}
                @sl-change=${async (e) => {
                  await api_put(`user/${user.uuid}`, { roles: [e.target.value] });
                  this.users = await api_get('user');
                }}
              >
                <sl-radio value="admin">Admin</sl-radio>
                <sl-radio value="user">User</sl-radio>
                <sl-radio value="guest">Guest</sl-radio>
              </sl-radio-group>
            </td>
            <td><sl-relative-time date="${user.created_at}Z"></sl-relative-time></td>
            <td><sl-relative-time date="${user.updated_at}Z"></sl-relative-time></td>
            <td align="center">
              <sl-checkbox
                ?checked=${user.disabled}
                @sl-change=${async (e) => {
                  await api_put(`user/${user.uuid}`, { disabled: e.target.checked });
                  this.users = await api_get('user');
                }}
              ></sl-checkbox>
            </td>
          </tr>
        `
      )}
    </table>`;
  }

  apikeyTemplate() {
    const keys = this.keys;
    return html`
      <table class="zebra-table">
        <tr>
          <td>Created</td>
          <td>Expires</td>
          <td>Disabled</td>
        </tr>
        ${keys.map(
          (key: any) =>
            html` <tr class=${key.disabled ? 'disabled' : ''}>
              <td><sl-relative-time date="${key.created_at}Z"></sl-relative-time></td>
              <td>
                <sl-input
                  type="datetime-local"
                  value=${key.expires_at.slice(0, -3)}
                  @sl-change=${async (e) => {
                    await api_put(`api_key/${key.uuid}`, { expires_at: e.target.value + 'Z' });
                    this.keys = await api_get('api_key');
                  }}
                ></sl-input>
              </td>
              <td align="center">
                <sl-checkbox
                  ?checked=${key.disabled}
                  @sl-change=${async (e) => {
                    await api_put(`api_key/${key.uuid}`, { disabled: e.target.checked });
                    this.keys = await api_get('api_key');
                  }}
                ></sl-checkbox>
              </td>
            </tr>`
        )}
      </table>
    `;
  }

  envTemplate() {
    const env = this.env;
    return html`
      <table class="zebra-table">
        ${Object.keys(env).map(
          (key) =>
            html`<tr>
              <td>${key}</td>
              <td>${env[key]}</td>
            </tr>`
        )}
      </table>
    `;
  }

  connectionsTemplate() {
    const connections = this.connections;
    return html`
      <table class="zebra-table">
        <tr>
          <td>Client Address</td>
          <td>Connected</td>
          <td>User / Tree</td>
        </tr>
        ${Object.values(connections).map(
          (key: any) =>
            html`<tr>
              <td>${key.param.client_addr}</td>
              <td align="center"><sl-checkbox readonly ?checked=${key.connected}></sl-checkbox></td>
              <td>${key.param.user || key.param.client_addr}</td>
            </tr>`
        )}
      </table>
    `;
  }

  superuserTemplate() {
    return html` <sl-tab-group placement="start">
      <sl-tab slot="nav" panel="me">Me</sl-tab>
      <sl-tab slot="nav" panel="users">Users</sl-tab>
      <sl-tab slot="nav" panel="api_key">Api Keys</sl-tab>
      <sl-tab slot="nav" panel="connections">Connections</sl-tab>
      <sl-tab slot="nav" panel="env">Env</sl-tab>

      <sl-tab-panel name="me">${this.meSettingsTemplate()}</sl-tab-panel>
      <sl-tab-panel name="users">${this.usersTemplate()}</sl-tab-panel>
      <sl-tab-panel name="api_key">${this.apikeyTemplate()}</sl-tab-panel>
      <sl-tab-panel name="connections">${this.connectionsTemplate()}</sl-tab-panel>
      <sl-tab-panel name="env">${this.envTemplate()}</sl-tab-panel>
    </sl-tab-group>`;
  }

  mainTemplate() {
    const me = this.settings.me;
    return me.superuser ? this.superuserTemplate() : this.meSettingsTemplate();
  }

  render() {
    return html`
      <leaf-page>
        <nav slot="nav">Settings</nav>
        <main>${this.mainTemplate()}</main>
      </leaf-page>
    `;
  }
}
