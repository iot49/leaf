import { Router } from '@lit-labs/router';
import { css, html } from 'lit';
import { customElement } from 'lit/decorators.js';
import { escapeHtml } from './app/dialog';
import { LeafBase } from './leaf-base';
import { LeafContext } from './leaf-context';

@customElement('leaf-main')
export class LeafMain extends LeafContext {
  static styles = [
    ...LeafBase.styles,
    css`
      #spinner-container {
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
      }
      .row {
        width: auto;
        border: 1px solid blue;
      }
    `,
  ];

  public router = new Router(this, [
    { path: '/ui/home', render: () => html`<h1>Home again!</h1>` },
    { path: '/ui/api', render: () => html`<leaf-api></leaf-api>` },
    {
      path: '/ui/trees',
      render: () => html`<leaf-trees></leaf-trees>`,
    },
    {
      path: '/ui/tree/:uuid',
      render: ({ uuid }) => html`<leaf-tree uuid=${uuid}></leaf-tree>`,
    },
    {
      path: '/ui/accounts',
      render: () => html`<leaf-accounts></leaf-accounts>`,
    },
    {
      path: '/ui/view/:view_id',
      render: ({ view_id }) => html`<leaf-view view_id=${parseInt(view_id)}></leaf-view>`,
    },
    { path: '/ui/log', render: () => html`<leaf-log></leaf-log>` },
    { path: '/ui/flash', render: () => html`<leaf-flash></leaf-flash>` },
    { path: '/ui/exec', render: () => html`<leaf-exec></leaf-exec>` },
    {
      path: '/ui/enter/:params',
      render: (params) => html`<h1>Enter ${JSON.stringify(params)}</h1>`,
      enter: async (params) => {
        console.log('enter', params);
        return true;
      },
    },
    { path: '/*', render: () => html`<leaf-trees></leaf-trees>` },
  ]);

  async connectedCallback(): Promise<void> {
    super.connectedCallback();
    globalThis.leaf = {};
    globalThis.leaf.router = this.router;
  }

  spinner(msg: string) {
    return html`
      <div id="spinner-container">
        <div class="row"><sl-spinner style="font-size: 50px; --track-width: 10px;"></sl-spinner></div>
        <div class="row">${escapeHtml(msg)}</div>
      </div>
    `;
  }

  render() {
    console.log('main.render', (this.router as any)._currentRoute.path, this.router.routes);
    if (!this.settings) return this.spinner('Loading settings from cache...');
    if (!this.connected) {
      this.router.goto('/');
    } else if (!this.config) {
      return this.spinner('Fetching configuration from server...');
    }
    return html`<main>${this.router.outlet()}</main>`;
  }
}
