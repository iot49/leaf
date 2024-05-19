import { css, html } from 'lit';
import { customElement } from 'lit/decorators.js';

import { api_get } from './app/api';
import { domain } from './app/env';
import { LeafBase } from './leaf-base';

@customElement('leaf-config-editor')
export class LeafConfigEditor extends LeafBase {
  static styles = [
    ...LeafBase.styles,
    css`
      iframe {
        width: 100vw;
        height: 100%;
      }
    `,
  ];

  render() {
    if (location.hostname === 'localhost') {
      console.log('Edit config on server only!');
      return html`Edit onfiguration on <a href=${`https://${domain}`}>server</a> only!`;
    }
    return html`
      <leaf-page>
        <nav slot="nav">Config Editor <sl-button @click=${async (_) => await api_get('update_config')}>Commit</sl-button></nav>

        <main>
          <iframe src=${`https://editor.${domain}`} title="Leaf configuration editor"></iframe>
        </main>
      </leaf-page>
    `;
  }
}
