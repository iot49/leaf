import { consume } from '@lit/context';
import { css, html } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { choose } from 'lit/directives/choose.js';
import { Config, configContext } from '../app/context/contexts';
import { LeafBase } from '../leaf-base';

const default_view = {
  title: 'All',
  icon: 'home-thermometer-outline',
  cards: [
    {
      title: 'All',
      type: 'entities',
      entities: [
        {
          entity_id: '*',
        },
      ],
    },
  ],
};

@customElement('leaf-view')
export class LeafView extends LeafBase {
  static styles = [
    ...LeafBase.styles,
    css`
      * {
        text-decoration: none;
      }
      nav {
        display: flex;
      }
      nav > div {
        margin-right: 1rem;
      }
      .selected {
        border-bottom: 2px solid var(--sl-color-neutral-0);
      }
    `,
  ];

  @consume({ context: configContext, subscribe: true })
  @property({ attribute: false })
  private config: Config;

  @property({ type: Number })
  view_id = 0;

  render() {
    let views, cards;
    try {
      views = this.config.views;
      cards = views[this.view_id].cards;
    } catch (e) {
      cards = default_view.cards;
      /*
      alertDialog(`View ${this.view_id} not found`, e.message);
      console.log('views', views);
      console.log('config', this.config);
      return html`view/${this.view_id} not found in <code>${JSON.stringify(this.config, null, 2)}</code>`;
      */
    }
    return html` <leaf-page mobile>
      <nav slot="nav">
        ${views.map(
          (view, index) =>
            html` <div @click=${() => this.goto(`view/${index}`)} class="${index == this.view_id ? 'selected' : ''}">
              <sl-icon library="mdi" name="${view.icon}"></sl-icon>
            </div>`
        )}
      </nav>
      ${cards.map((card) =>
        choose(
          card.type,
          [['entities', () => html`<leaf-entities .card=${card}></leaf-entities>`]],
          () => html`<h1>Unknown card type: ${card.type}</h1>`
        )
      )}
    </leaf-page>`;
  }
}
