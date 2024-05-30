import { css, html } from 'lit';
import { customElement, property } from 'lit/decorators.js';

import { consume } from '@lit/context';
import { logout } from './app/api';
import { Connected, connectedContext, Settings, settingsContext } from './app/context/contexts';
import { api_url, domain } from './app/env';
import { LeafBase } from './leaf-base';

@customElement('leaf-page')
export class LeafPage extends LeafBase {
  @property({ type: Boolean })
  mobile: boolean = false;

  @consume({ context: connectedContext, subscribe: true })
  @property({ attribute: false })
  private connected: Connected;

  @consume({ context: settingsContext, subscribe: true })
  @property({ attribute: false })
  private settings: Settings;

  constructor() {
    super();
  }

  static styles = [
    ...LeafBase.styles,
    css`
      .page {
        box-sizing: content-box;
        height: 100vh;
        width: 100vw;
        display: flex;
        flex-direction: column;
      }

      nav {
        box-sizing: content-box;
        height: var(--page-header-height);
        display: flex;
        flex: 0 0 auto;
        align-items: center;
        line-height: 1rem;
        padding: 0 0.8rem;
        background-color: var(--sl-color-primary-500);
        color: white;
        font-weight: 500;
        font-size: 150%;
      }

      main {
        box-sizing: content-box;
        height: calc(100vh - var(--page-header-height));
        display: flex;
        flex: 1 1 auto;
        color: var(--sl-color-neutral-1000);
        background-color: var(--sl-color-neutral-0);
      }

      .nav-slot {
        display: flex;
        flex: 1 1 auto;
        justify-content: center;
      }

      .leaf-icon,
      .menu > sl-icon {
        border-radius: 50%;
        justify-content: flex-start;
      }
      .leaf-icon:hover,
      .menu > sl-icon:hover {
        background-color: var(--sl-color-primary-600);
      }

      .menu {
        display: flex;
        flex: 0 0 auto;
        justify-content: flex-end;
        padding-right: 0.2em;
        color: var(--sl-color-neutral-0);
      }
      .menu > sl-icon {
        color: white;
      }

      .dropdown {
        display: none;
        position: absolute;
        right: 0.5rem;
        top: 2rem;
        bottom: auto;
        z-index: 1000;
      }
      .menu:hover .dropdown {
        display: inline;
      }
      sl-menu-item {
        display: flex;
        align-items: center;
      }
      sl-menu-item > sl-icon {
        margin-right: 20px;
        font-size: 18px;
      }

      .mobile > nav > .leaf-icon {
        display: none;
      }

      .mobile > nav > .nav-slot {
        justify-content: flex-start;
      }

      .connected {
        font-size: var(--sl-font-size-small);
        position: absolute;
        top: 3px;
        right: 3px;
      }

      @media screen and (max-width: 450px) {
        .mobile {
          flex-direction: column-reverse;
          background-color: yellow;
        }
        .mobile .dropdown {
          background-color: pink;
          top: auto;
          bottom: 2rem;
        }
      }
    `,
  ];

  async action(target: string) {
    if (target === 'logout') {
      logout();
    } else if (target.startsWith('!')) {
      location.href = `https://${target.slice(1)}.${domain}`;
    } else if (target === 'api') {
      location.href = `${api_url}/docs`;
    } else if (target === 'docs') {
      location.href = `https://iot49.org`;
    } else {
      await this.goto(target);
    }
  }

  nav_menu() {
    // we use the html element id to specify the path (see action, above)
    const nav = [
      { id: 'trees', icon: 'forest-outline', text: 'Trees' },
      { id: 'log', icon: 'math-log', text: 'Log', disabled: !this.connected },
      { id: 'settings', icon: 'cog', text: 'Settings', hide: !this.settings.me.superuser },
      { id: 'config', icon: 'microsoft-visual-studio-code', text: 'Configuration', disabled: !this.connected },
      // { id: '!editor', icon: 'microsoft-visual-studio-code', text: 'Editor' },
      { id: '!jupyter', icon: 'code-block-braces', text: 'Jupyter' },
      { id: '!homeassistant', icon: 'home-lightbulb-outline', text: 'Homeassistant' },
      { id: 'docs', icon: 'book-open', text: 'Docs' },
      { id: 'api', icon: 'book-open', text: 'Api' },
      { id: 'logout', icon: 'logout', text: 'Logout' },
    ];

    return html`
      <div class="menu">
        <sl-icon library="mdi" name="dots-vertical"></sl-icon>
        <div class="dropdown">
          <sl-menu @click=${async (e) => await this.action(e.target.id)}>
            ${nav.map((item) =>
              item.hide
                ? html``
                : html`
                    <sl-menu-item id=${item.id} ?disabled=${item.disabled}>
                      <sl-icon library="mdi" name=${item.icon}></sl-icon>${item.text}
                    </sl-menu-item>
                  `
            )}
          </sl-menu>
        </div>
      </div>
    `;
  }

  render() {
    return html`
      <div class="page ${this.mobile ? 'mobile' : ''}">
        <nav>
          <!-- left icon (go to root) -->
          <div class="leaf-icon">
            <sl-icon library="mdi" @click=${async (_) => await this.goto('view/0')} name="leaf-maple"></sl-icon>
          </div>
          <!-- parent nav items -->
          <div class="nav-slot"><slot name="nav"></slot></div>
          <!-- right top menu -->
          ${this.nav_menu()}
          <sl-icon library="mdi" class="connected" name=${this.connected ? 'wifi' : 'wifi-off'}></sl-icon>
        </nav>
        <!-- page content -->
        <main>
          <slot></slot>
        </main>
      </div>
    `;
  }
}
