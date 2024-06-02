import { EventEmitter, IEventEmitter } from '../event-emitter';
import { Transport } from './eventbus';

export class BleBus extends EventEmitter implements IEventEmitter, Transport {
  public treeId: string;

  constructor(tree_id: string) {
    super();
    this.treeId = tree_id;
  }

  public get connected(): boolean {
    return false;
  }

  public async send(msg: string): Promise<void> {
    console.log('BleBus.post_event - not implemented', msg);
  }

  public disconnect() {}
}
