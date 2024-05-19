import { consume } from '@lit/context';
import { css, html } from 'lit';
import { customElement, property } from 'lit/decorators.js';

import { type Log, logContext } from './app/context/contexts';
import { LeafBase } from './leaf-base';

@customElement('leaf-log')
export class LeafLog extends LeafBase {
  @consume({ context: logContext, subscribe: true })
  @property({ attribute: false })
  private log: Log;

  static styles = [
    ...LeafBase.styles,
    css`
      main {
        display: flex;
        flex-direction: column;
        overflow: auto;
        padding: 3px;
        font-size: 13px;
        line-height: 1.3;
        font-family: 'menlo', consolas, 'DejaVu Sans Mono', monospace;
      }

      .entry {
        display: flex;
      }
      span {
        display: flex;
        margin-right: 1rem;
        margin-bottom: 5px;
      }
      .timestamp {
        flex: 0 0 11rem;
      }
      .level {
        flex: 0 0 5rem;
      }
      .name {
        flex: 0 0 10rem;
      }
      .message {
        flex: 0 0 auto;
        display: block;
        white-space: pre-wrap;
        word-break: break-all;
        word-wrap: break-word;
      }
    `,
  ];

  entry_template(entry) {
    const date = new Date(0);
    date.setUTCSeconds(entry.timestamp);
    return html`
      <div class="entry">
        <span class="timestamp">${date.toISOString().split('.')[0]}</span>
        <span class="level">${entry.levelname}</span>
        <span class="name">${entry.name}</span>
        <span class="message">${entry.message}</span>
      </div>
    `;
  }

  render() {
    return html`
      <leaf-page>
        <nav slot="nav">Log</nav>

        <main>${this.log.map((log_entry) => this.entry_template(log_entry))}</main>
      </leaf-page>
    `;
  }
}
