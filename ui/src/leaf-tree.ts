import { consume } from '@lit/context';
import { SlDialog, SlSelect, SlTabGroup } from '@shoelace-style/shoelace';
import { css, html } from 'lit';
import { customElement, property, query, state } from 'lit/decorators.js';
import { api_delete, api_get, api_post, api_put } from './app/api';
import { Config, configContext, Settings, settingsContext } from './app/context/contexts';
import { alertDialog, confirmDialog, promptDialog } from './app/dialog';
import { get_resource } from './app/github-releases';
import { flash_esp } from './app/mpexec/flash_esp';
import { MpExec } from './app/mpexec/mpexec';
import { LeafBase } from './leaf-base';

@customElement('leaf-tree')
export class LeafTree extends LeafBase {
  static styles = [
    ...LeafBase.styles,
    css`
      main {
        margin: 1rem;
      }
      #create_button {
        margin-top: 2rem;
        float: right;
      }
      .branches-title {
        margin-top: 2rem;
      }
      .td-item {
        font-weight: bold;
        margin-right: 2rem;
        padding-right: 2rem;
      }
      #device-id sl-input::part(base) {
        background-color: var(--sl-color-neutral-100);
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
      .title {
        min-width: 300px;
      }
      .branch_id {
        max-width: 100px;
      }
    `,
  ];

  @consume({ context: settingsContext, subscribe: true })
  @property({ attribute: false })
  private settings: Settings;

  @consume({ context: configContext, subscribe: true })
  @property({ attribute: false })
  private config: Config;

  @property() uuid: string;
  @state() tree: any;
  @state() releases: any;

  @query('#enroll') enrollDialog: SlDialog;
  @query('#enroll-tabs') enrollTabs: SlTabGroup;

  async connectedCallback() {
    super.connectedCallback();
    this.tree = await api_get(`tree/${this.uuid}`);
    this.releases = await get_resource();
  }

  render() {
    if (!this.tree || !this.releases) {
      return html`<sl-spinner style="font-size: 50px; --track-width: 10px;"></sl-spinner>`;
    } else {
      const me = this.settings.me;
      const admin = me.roles.includes('admin');
      const tree = this.tree;
      return html`${this.enrollTemplate()}
        <leaf-page>
          <nav slot="nav">Tree Details</nav>
          <main>
            <table class="tree-details">
              <tr>
                <td class="td-item" align="right">ID</td>
                <td>${tree.tree_id}</td>
              </tr>
              <tr>
                <td class="td-item" align="right">Title</td>
                <td>${tree.title}</td>
              </tr>
              <tr>
              <td class="td-item" align="right">Created</td>
                <td><sl-relative-time date="${tree.created_at}Z"></sl-relative-time></td>
              </tr>
              <td class="td-item" align="right">Updated</td>
                <td><sl-relative-time date="${tree.updated_at}Z"></sl-relative-time></td>
              </tr>
              <tr>
                <td class="td-item" align="right">Disabled</td>
                <td>
                  <sl-checkbox
                    ?checked=${tree.disabled}
                    @sl-change=${async (e) => {
                      await api_put(`tree/${tree.uuid}`, { disabled: e.target.checked });
                      this.tree = await api_get(`tree/${this.uuid}`);
                      this.settings.me = await api_get('me');
                    }}
                    >Disabled</sl-checkbox
                  >
                </td>
              </tr>
            </table>

            ${
              tree.branches.length === 0
                ? html``
                : html` <h1 class="branches-title">Branches</h1>
                    <table class="zebra-table">
                      ${this.tree.branches.map(
                        (branch: any) =>
                          html` <tr class=${branch.disabled ? 'disabled' : ''}>
                            <td>
                              <sl-input
                                class=${'branch_id ' + branch.disabled ? 'disabled' : ''}
                                value=${branch.branch_id}
                                ?readonly=${!admin}
                                @sl-change=${async (e) => {
                                  await api_put(`branch/${branch.uuid}`, { branch_id: e.target.value });
                                  this.tree = await api_get(`tree/${this.uuid}`);
                                }}
                              ></sl-input>
                            </td>
                            <td>
                              <sl-input
                                class=${'title ' + branch.disabled ? 'disabled' : ''}
                                value=${branch.title}
                                ?readonly=${!admin}
                                @sl-change=${async (e) => {
                                  await api_put(`branch/${branch.uuid}`, { title: e.target.value });
                                  this.tree = await api_get(`tree/${this.uuid}`);
                                }}
                              ></sl-input>
                            </td>
                            <td><sl-input value=${branch.mac} readonly></sl-input></td>
                            <td>
                              <sl-checkbox
                                ?checked=${branch.disabled}
                                @sl-change=${async (e) => {
                                  await api_put(`branch/${branch.uuid}`, { disabled: e.target.checked });
                                  this.tree = await api_get(`tree/${this.uuid}`);
                                }}
                                >Disabled</sl-checkbox
                              >
                            </td>
                            <td>
                              <sl-icon-button
                                library="mdi"
                                name="delete"
                                ?disabled=${!admin}
                                @click=${async (_) => {
                                  if (await confirmDialog(`Delete ${branch.branch_id}`, 'This operation cannot be undone.', 'Delete', 'danger')) {
                                    await api_delete(`branch/${branch.uuid}`);
                                    this.tree = await api_get(`tree/${this.uuid}`);
                                  }
                                }}
                              ></sl-icon-button>
                            </td>
                          </tr>`
                      )}
                    </table>`
            }
            <sl-button
              id="create_button"
              variant="primary"
              size="large"
              circle
              @click=${async (_) => {
                const branch_id = await promptDialog('Create Branch', {
                  label: 'ID (unique)',
                  helpText: 'alphanumeric characters and underscores only',
                  pattern: '[a-z0-9_]+$',
                  required: true,
                  clearable: true,
                });
                if (tree.branches.find((branch: any) => branch.branch_id === branch_id)) {
                  alertDialog('Duplicate', 'A branch with this ID already exists');
                  return;
                }
                (this.enrollDialog as any).branch_id = branch_id;
                this.enrollDialog.show();
              }}
            >
              <sl-icon library="mdi" name="plus" style="font-size: 30px"></sl-icon>
            </sl-button>
          </main>
        </leaf-page>`;
    }
  }

  enrollTemplate() {
    return html`
      <sl-dialog id="enroll" label="Enroll New Branch" style="--width: 80vw;">
        <sl-tab-group id="enroll-tabs" placement="start">
          <sl-tab slot="nav" panel="flash">Setup</sl-tab>
          <sl-tab slot="nav" panel="flashing">Flashing ...</sl-tab>
          <sl-tab slot="nav" panel="uid">Read MAC Address</sl-tab>
          <sl-tab slot="nav" panel="register">Register with Earth</sl-tab>

          <!-- SETUP -->
          <sl-tab-panel name="flash">
            <h3>Flash Firmware</h3>
            <sl-select id="firmware" label="Chooose Firmware" value="0">
              ${this.releases.map((release: any, index: number) => {
                return html`<sl-option value=${index}>${release.name}</sl-option><a href="https://github.com/iot49/leaf/commits/">Change Log</a>`;
              })}
            </sl-select>
            <p>Connect the device to the computer with a USB cable.</p>
            <p>
              Then put it into bootloader mode. On the ESP32-S3 this usually requires pressing and holding down the BOOT button, then briefly pressing
              and releasing RESET, finally letting go BOOT.
            </p>
            <sl-button @click=${(_) => this.enrollTabs.show('uid')}>Skip</sl-button>
            <sl-button variant="primary" @click=${async (_) => await this.flash()}>Flash</sl-button>
          </sl-tab-panel>

          <!-- FLASHING -->
          <sl-tab-panel name="flashing">
            <h3>Flashing ...</h3>
            <div id="flash_param"></div>
            <div id="flash_progress"></div>
          </sl-tab-panel>

          <!-- UID -->
          <sl-tab-panel name="uid">
            <h3>Configure Device</h3>
            <p>Connect the device with a USB cable.</p>
            <sl-button
              variant="primary"
              @click=${async (_) => {
                if (await this.registerDevice()) this.enrollTabs.show('register');
              }}
              >Connect</sl-button
            >
          </sl-tab-panel>

          <!-- REGISTER: read mac, write config to device, device will contact server and complete registration -->
          <sl-tab-panel name="register">
            <h3>Provision Device & register with Earth</h3>
            <p>Device is connecting to the earth and completing the registration.</p>
            <p>
              The status LED will blink fast when it is connected to the internet, slowly once it has connected to the earth, and stay on solid green
              when the registration is complete.
            </p>
            <sl-button variant="primary" @click=${(_) => this.enrollDialog.hide()}>Done</sl-button>
          </sl-tab-panel>
        </sl-tab-group>
      </sl-dialog>
    `;
  }

  async flash() {
    // choose firmware, flash, reset
    const firmware_id: any = (this.shadowRoot.querySelector('#firmware') as SlSelect).value;
    const release: any = this.releases[firmware_id];
    const asset = release.assets.find((asset: any) => asset.name === 'firmware.bin');
    console.log('firmware url', asset.size, asset.created_at, asset.browser_download_url);
    this.enrollTabs.show('flashing');
    var headers = {
      Accept: 'application/octet-stream',
    };

    const response = await fetch('http://cors.io/?https://github.com/iot49/leaf/blob/main/LICENSE', {
      method: 'GET',
      headers: headers,
    });
    const binary = await response.blob();
    console.log('binary', binary.size, binary);
    await flash_esp(asset.browser_download_url, (i, bytesSent, totalBytes) => {
      console.log('progress', i, bytesSent, totalBytes);
    });
  }

  async registerDevice(): Promise<boolean> {
    const branch_id = (this.enrollDialog as any).branch_id;
    // connect
    const mpexec = new MpExec();
    await mpexec.openDevice('s3', false);
    // read mac
    let mac = await mpexec.exec(`
import machine
mac = machine.unique_id()
print(":".join("{:02x}".format(x) for x in mac))`);
    mac = mac[0].slice(0, -2);
    if (this.tree.branches.find((branch: any) => branch.mac === mac)) {
      alertDialog('Device is already registered', `Branch '${mac}' is already registered with '${this.tree.tree_id}'`);
      await mpexec.close();
      return false;
    }
    // create new branch
    await api_post('branch', {
      branch_id: branch_id,
      tree_uuid: this.tree.uuid,
      title: `Branch ${branch_id}`,
      mac: mac,
    });
    this.tree = await api_get(`tree/${this.uuid}`);
    // get gateway_secrets and write to branch
    const secrets = await api_get(`gateway_secrets/${this.tree.uuid}`);
    let code = `
with open("secrets.json", "w") as f:
    f.write("""${JSON.stringify(secrets)}""")`;
    await mpexec.exec(code);
    // write config to branch
    code = `
with open("config.json", "w") as f:
    f.write("""${JSON.stringify(this.config)}""")`;
    await mpexec.exec(code);

    await mpexec.close();
    return true;
  }
}
