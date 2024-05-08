import { consume } from '@lit/context';
import 'lit';
import { css, html } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { api_delete, api_get, api_post, api_put } from './app/api';
import { Connected, connectedContext, Settings, settingsContext } from './app/context/contexts';
import { alertDialog, confirmDialog, promptDialog } from './app/dialog';
import { eventbus } from './app/eventbus/eventbus';
import { LeafBase } from './leaf-base';

@customElement('leaf-trees')
export class LeafTrees extends LeafBase {
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
      .tree_id {
        max-width: 100px;
      }
      #earth {
        background-color: var(--sl-color-primary-300);
      }
      #table-gap td {
        padding-bottom: 10px;
        background-color: var(--sl-color-neutral-0);
      }
    `,
  ];

  @consume({ context: settingsContext, subscribe: true })
  @property({ attribute: false })
  private settings: Settings;

  @consume({ context: connectedContext, subscribe: true })
  @property({ attribute: false })
  private connected: Connected;

  render() {
    const me = this.settings.me;
    const admin = me.roles.includes('admin');
    return html`
      <leaf-page>
        <nav slot="nav">Trees</nav>
        <main>
          <table class="zebra-table">
            <tr id="earth">
              <td>earth</td>
              <td><sl-input value="Cloud Server" readonly></sl-input></td>
              <td align="right">
                <sl-icon-button library="mdi" name="wifi" @click=${(_) => eventbus.connect('#earth')}></sl-icon-button>
              </td>
            </tr>
            <tr id="table-gap">
              <td></td>
            </tr>
            ${me.trees.map(
              (tree: any) => html`
                <tr class=${tree.disabled ? 'disabled' : ''}>
                  <td>
                    <sl-input
                      class="tree_id"
                      value=${tree.tree_id}
                      ?readonly=${!admin}
                      @sl-change=${async (e) => {
                        await api_put(`tree/${tree.uuid}`, { tree_id: e.target.value });
                        this.settings.me = await api_get('me');
                      }}
                    ></sl-input>
                  </td>
                  <td>
                    <sl-input
                      class="title"
                      value=${tree.title}
                      ?readonly=${!admin}
                      @sl-change=${async (e) => {
                        await api_put(`tree/${tree.uuid}`, { title: e.target.value });
                        this.settings.me = await api_get('me');
                      }}
                    ></sl-input>
                  </td>
                  <td>
                    <sl-icon-button
                      library="mdi"
                      name="delete"
                      ?disabled=${!admin}
                      @click=${async (_) => {
                        if (await confirmDialog(`Delete ${tree.tree_id}`, 'This operation cannot be undone.', 'Delete', 'danger')) {
                          await api_delete(`tree/${tree.uuid}`);
                          this.settings.me = await api_get('me');
                        }
                      }}
                    ></sl-icon-button>
                    <sl-icon-button
                      library="mdi"
                      name="pencil"
                      ?disabled=${!this.connected}
                      @click=${(_) => this.goto(`tree/${tree.uuid}`)}
                    ></sl-icon-button>
                    <sl-icon-button library="mdi" name="bluetooth" ?disabled=${tree.disabled} @click=${(_) => console.log('BT')}></sl-icon-button>
                    <sl-icon-button library="mdi" name="wifi" ?disabled=${tree.disabled} @click=${(_) => console.log('Wifi')}></sl-icon-button>
                  </td>
                </tr>
              `
            )}
          </table>
          ${admin
            ? html`<sl-button
                id="create_button"
                variant="primary"
                size="large"
                circle
                @click=${async (_) => {
                  const tree_id = await promptDialog('Create Tree', {
                    label: 'ID (unique)',
                    helpText: 'alphanumeric characters and underscores only',
                    pattern: '[a-z0-9_]+$',
                    required: true,
                    clearable: true,
                  });
                  if (tree_id === undefined) return;
                  if (me.trees.find((tree: any) => tree.tree_id === tree_id)) {
                    alertDialog('Duplicate', `A tree with this ID already exists`);
                    return;
                  }
                  await api_post('tree', { tree_id: tree_id, title: `Tree ${tree_id}` });
                  this.settings.me = await api_get('me');
                }}
              >
                <sl-icon library="mdi" name="plus" style="font-size: 30px"></sl-icon>
              </sl-button>`
            : html``}
        </main>
      </leaf-page>
    `;
  }
}
