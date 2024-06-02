export interface IEventEmitter {
  /**
   * Register a callback for one or more events.
   * Usage: EventEmitter.on('event1', 'event2', callback);
   */
  on(...args: any[]): void;

  /**
   * Unregister a callback for an event.
   * Usage: EventEmitter.off('event', callback);
   */
  off(event: string, callback: Function): void;

  /**
   * Unregister all callbacks.
   */
  clear(): void;

  /**
   * Emit an event with optional data.
   * Usage: EventEmitter.emit('event', data);
   */
  emit(event: string, ...data: any[]): void;
}

export class EventEmitter implements IEventEmitter {
  protected eventMap: Map<string, Function[]>;

  constructor() {
    this.eventMap = new Map();
  }

  on(...args) {
    const events = args.slice(0, -1);
    const callback = args[args.length - 1];
    for (const event of events) {
      if (!this.eventMap.has(event)) {
        this.eventMap.set(event, []);
      }
      if (this.eventMap.get(event).includes(callback)) console.warn('EventEmitter.on: callback already registered');
      this.eventMap.get(event).push(callback);
    }
  }

  off(event, callback) {
    if (this.eventMap.has(event)) {
      const callbacks = this.eventMap.get(event).filter((cb) => cb !== callback);
      this.eventMap.set(event, callbacks);
    }
  }

  clear() {
    this.eventMap.clear();
  }

  emit(event, ...data) {
    if (this.eventMap.has(event)) {
      this.eventMap.get(event).forEach((callback) => {
        setTimeout(() => callback(...data), 0);
      });
    }
  }
}
