import 'lit';
import { css, html } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import { api_get, api_put } from './app/api';
import { LeafBase } from './leaf-base';

@customElement('leaf-accounts')
export class LeafAccounts extends LeafBase {
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
    `,
  ];

  @state()
  private users: any = [];

  @state()
  private keys: any = [];

  async connectedCallback() {
    super.connectedCallback();
    this.users = await api_get(`user`);
    this.keys = await api_get(`api_key`);
  }

  render() {
    const users = this.users;
    const keys = this.keys;
    return html`
      <leaf-page>
        <nav slot="nav">Users</nav>
        <main>
          <h1>Users</h1>
          <table class="zebra-table">
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
          </table>

          <h1>API Keys</h1>
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
        </main>
      </leaf-page>
    `;
  }
}
