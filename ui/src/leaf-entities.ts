import { consume } from '@lit/context';
import { html, PropertyValueMap } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { State, stateContext } from './app/context/contexts';
import { LeafBase } from './leaf-base';

@customElement('leaf-entities')
export class LeafEntities extends LeafBase {
  @property({ attribute: false })
  card: any;

  @consume({ context: stateContext, subscribe: true })
  @property({ attribute: false })
  state: State;

  number_of_entities = 0;

  protected shouldUpdate(_changedProperties: PropertyValueMap<any> | Map<PropertyKey, unknown>): boolean {
    return _changedProperties.size > 0 || this.state.size != this.number_of_entities;
  }

  render() {
    this.number_of_entities = this.state.size;
    const templates: any[] = [];
    for (const spec of this.card.entities) {
      const rule = spec.entity_id;
      const keys = this.state.keys();
      for (const eid of keys) {
        if (this.wildcard_match(eid, rule)) {
          templates.push(html`<leaf-entity entity_id=${eid} .spec=${spec}></leaf-entity>`);
        }
      }
    }
    return html`
      <ul>
        ${templates}
      </ul>
    `;
  }

  wildcard_match(str, rule) {
    var escapeRegex = (str) => str.replace(/([.*+?^=!:${}()|\[\]\/\\])/g, '\\$1');
    return new RegExp('^' + rule.split('*').map(escapeRegex).join('.*') + '$').test(str);
  }
}
