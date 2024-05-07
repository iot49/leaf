import { createContext } from '@lit/context';

export type Connected = Boolean;
export const connectedContext = createContext<Connected>(Symbol('connected'));

// eventbus CurrentState
import { type State } from '../eventbus/state';
export { type State } from '../eventbus/state';
export const stateContext = createContext<State>(Symbol('state'));

// eventbus Config
export type Config = any;
export const configContext = createContext<Config>(Symbol('config'));

// eventbus Log
export type Log = Array<any>;
export const logContext = createContext<Log>(Symbol('log'));

// browser Settings (indexedDB)
export type Settings = any;
export const settingsContext = createContext<Settings>(Symbol('settings'));
