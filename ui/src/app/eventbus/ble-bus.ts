import { Bus } from "./eventbus";

export class BleBus implements Bus {
  public tree_id: string;

  constructor(tree_id: string) {
    this.tree_id = tree_id;
  }

  public async postEvent(event: object) {
    console.log("BleBus.post_event - not implemented", event);
  }

  public disconnect() {}

  public get connected(): boolean {
    return false;
  }
}
