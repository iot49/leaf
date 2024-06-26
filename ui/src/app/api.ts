import { api_url } from './env';
import { FetchError } from './errors';

export async function api_get(resource: string = '', requestOptions = {}, path = 'api'): Promise<object> {
  try {
    const url = `${api_url}/${path}/${resource}`;
    console.log('api_get', url);
    const response = await fetch(url, requestOptions);
    if (response.ok) {
      return await response.json();
    } else if (response.status === 404) {
      // {"detail":"Not found"}
      console.log('api_get 404', resource);
      const json = await response.json();
      console.log(`${resource} not found`, json.detail);
      // alertDialog(`${resource} not found`, json.detail);
      throw new FetchError(json.detail);
    } else if (response.status === 400) {
      // {"detail":"Missing required Cloudflare authorization token"}
      // force browser to reauthenticate with Cloudflare
      console.log('force reauthenticate', resource);
      window.open('/ui', '_self');
    } else {
      const text = await response.text();
      console.log('api_get error', response.status, text);
      console.log(`Unspecified error`, `Failed fetching ${resource}: ${text}`);
      //alertDialog(`Unspecified error`, `Failed fetching ${resource}: ${text}`);
      throw new FetchError(text);
    }
  } catch (error) {
    // Failed to fetch (offline?)
    console.log('api_get error', error.message);
    console.log('Offline?', 'Cannot connect to earth. Is the server running? Internet working?');
    // alertDialog('Offline?', 'Cannot connect to earth. Is the server running? Internet working?');
    throw new FetchError(error.message);
  }
  return undefined;
}

export async function api_post(resource: string = '', data: object = {}, requestOptions = {}): Promise<object> {
  return api_get(resource, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
    ...requestOptions,
  });
}

export async function api_put(resource: string = '', data: object = {}, requestOptions = {}) {
  return api_get(resource, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
    ...requestOptions,
  });
}

export async function api_delete(resource: string = '', requestOptions = {}) {
  return api_get(resource, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    ...requestOptions,
  });
}

export async function logout() {
  try {
    const CF_APP_LOGOUT_URL = '/cdn-cgi/access/logout';
    await fetch(CF_APP_LOGOUT_URL, { mode: 'no-cors' });
  } catch (error) {
    console.error('***** logout', error);
  }
  window.open('/ui', '_self');
}
