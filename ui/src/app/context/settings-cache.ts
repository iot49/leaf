import { getMany, set } from 'idb-keyval';

export class SettingsCache {
  private _settingsProvider; // context (declared in leaf-context)
  private _settingsLoaded = false;

  // decleare settings and default values
  private cache = {
    me: {
      email: 'nobody@example.com',
      roles: ['guest'],
      trees: [],
    },
    auto_connect: true,
    dark_theme: false,
  };

  public constructor(settingsProvider) {
    this._settingsProvider = settingsProvider;
    this._settingsLoaded = false;
  }

  public settings = new Proxy(
    {
      main: this,
    },
    {
      get(target, name, _) {
        // retrieve value from cache
        return target.main._settingsLoaded ? target.main.cache[name] : undefined;
      },
      set(target, name, value, _) {
        // update cache
        target.main.cache[name] = value;
        // update indexedDB
        set(name as string, value);
        // update context (defined in leaf-context)
        if (target.main._settingsLoaded) target.main._settingsProvider.setValue(target.main.settings, true);
        return true;
      },
    }
  ) as any;

  public async load() {
    const obj = await getMany(Object.keys(this.cache));
    // update cache with data loaded from indexedDB
    for (const [i, key] of Object.keys(this.cache).entries()) {
      if (obj[i]) this.cache[key] = obj[i];
    }
    this._settingsProvider.setValue(this.settings, true);
    this._settingsLoaded = true;
  }
}
