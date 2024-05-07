import { SlInput } from "@shoelace-style/shoelace";
import { html } from "lit";
import { customElement, state } from "lit/decorators.js";
import { LeafBase } from "./leaf-base";


@customElement("leaf-api")
export class LeafApi extends LeafBase {


    @state()
    json: object = {};

    render() {
        return html`
        <leaf-page>
            <nav slot="nav">API</nav>
            <main>
                DATA: <pre>${JSON.stringify(this.json, null, 2)}</pre>

                <sl-input id="resource" label="Resource, e.g. user" clearable></sl-input>
                <sl-button @click=${() => this.get_resource_helper()}>get resource NO HEADERS</sl-button>
                <sl-button @click=${() => this.logout()}>Logout /ui</sl-button>
                <sl-button @click=${() => window.open("/ui", "_self")}>open /ui</sl-button>
            </main>
        </leaf-page>
        `
    }

    async get_resource_helper() {
        const resource = (this.renderRoot.querySelector("#resource") as SlInput)
            .value;
        this.json = await this.api_get(resource);
        await this.api_get(resource);
    }
}