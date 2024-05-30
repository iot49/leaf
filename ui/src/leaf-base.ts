import { LitElement, css } from 'lit';
import { customElement } from 'lit/decorators.js';
import { LeafMain } from './leaf-main';
@customElement('leaf-base')
export class LeafBase extends LitElement {
  static styles = [
    css`
      * {
        box-sizing: border-box;
      }

      sl-icon::part(svg) {
        fill: currentColor;
      }

      .zebra-table td {
        padding: 1px 12px;
      }
      .zebra-table tr:nth-child(even) {
        background-color: var(--sl-color-neutral-100);
      }
      .zebra-table tr:nth-child(odd) {
        background-color: var(--sl-color-neutral-300);
      }
      .zebra-table tr:hover {
        background-color: var(--sl-color-emerald-300);
      }
    `,
  ];

  private static main: LeafMain;
  public static currentRoute: string = '';

  async goto(path: string = '') {
    if (!LeafBase.main) LeafBase.main = document.querySelector('leaf-main');
    LeafBase.currentRoute = path;
    await LeafBase.main.router.goto(`/ui/${path}`);
  }
}
