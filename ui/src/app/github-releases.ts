import { github_owner, github_repo } from './env';
import { FetchError } from './errors';

export async function get_resourceX(resource: string = 'releases'): Promise<any> {
  const response = await fetch(`https://api.github.com/repos/${github_owner}/${github_repo}/${resource}`, {
    headers: {
      'X-GitHub-Api-Version': '2022-11-28',
      Accept: 'application/vnd.github+json',
      // "Authorization:": `Bearer ${github_token}`,
    },
  });
  console.log(response);
  if (!response.ok) {
    throw new FetchError(`Failed downloading ${github_owner}/${github_repo}/${resource}, status: ${response.status}`);
  }
  return await response.json();
}

export async function get_asset(release: any, tag_name: string, asset_name: string = 'firmware.bin'): Promise<any> {
  if (release.tag_name === tag_name) {
    for (const asset of release.assets) {
      if (asset.name === asset_name) {
        return await get_resourceX(`releases/assets/${asset.id}`);
      }
    }
  }
}

export async function get_resource(_: string = 'releases'): Promise<any> {
  return [
    {
      url: 'https://api.github.com/repos/iot49/leaf/releases/156151879',
      assets_url: 'https://api.github.com/repos/iot49/leaf/releases/156151879/assets',
      upload_url: 'https://uploads.github.com/repos/iot49/leaf/releases/156151879/assets{?name,label}',
      html_url: 'https://github.com/iot49/leaf/releases/tag/v0.0.1',
      id: 156151879,
      author: {
        login: 'github-actions[bot]',
        id: 41898282,
        node_id: 'MDM6Qm90NDE4OTgyODI=',
        avatar_url: 'https://avatars.githubusercontent.com/in/15368?v=4',
        gravatar_id: '',
        url: 'https://api.github.com/users/github-actions%5Bbot%5D',
        html_url: 'https://github.com/apps/github-actions',
        followers_url: 'https://api.github.com/users/github-actions%5Bbot%5D/followers',
        following_url: 'https://api.github.com/users/github-actions%5Bbot%5D/following{/other_user}',
        gists_url: 'https://api.github.com/users/github-actions%5Bbot%5D/gists{/gist_id}',
        starred_url: 'https://api.github.com/users/github-actions%5Bbot%5D/starred{/owner}{/repo}',
        subscriptions_url: 'https://api.github.com/users/github-actions%5Bbot%5D/subscriptions',
        organizations_url: 'https://api.github.com/users/github-actions%5Bbot%5D/orgs',
        repos_url: 'https://api.github.com/users/github-actions%5Bbot%5D/repos',
        events_url: 'https://api.github.com/users/github-actions%5Bbot%5D/events{/privacy}',
        received_events_url: 'https://api.github.com/users/github-actions%5Bbot%5D/received_events',
        type: 'Bot',
        site_admin: false,
      },
      node_id: 'RE_kwDOL4ZmU84JTrBH',
      tag_name: 'v0.0.1',
      target_commitish: 'main',
      name: 'leaf MicroPython VM for ESP32_S3_N16R8 0.0.1',
      draft: false,
      prerelease: false,
      created_at: '2024-05-16T19:26:19Z',
      published_at: '2024-05-16T19:30:27Z',
      assets: [
        {
          url: 'https://api.github.com/repos/iot49/leaf/releases/assets/168357554',
          id: 168357554,
          node_id: 'RA_kwDOL4ZmU84KCO6y',
          name: 'firmware.bin',
          label: '',
          uploader: {
            login: 'github-actions[bot]',
            id: 41898282,
            node_id: 'MDM6Qm90NDE4OTgyODI=',
            avatar_url: 'https://avatars.githubusercontent.com/in/15368?v=4',
            gravatar_id: '',
            url: 'https://api.github.com/users/github-actions%5Bbot%5D',
            html_url: 'https://github.com/apps/github-actions',
            followers_url: 'https://api.github.com/users/github-actions%5Bbot%5D/followers',
            following_url: 'https://api.github.com/users/github-actions%5Bbot%5D/following{/other_user}',
            gists_url: 'https://api.github.com/users/github-actions%5Bbot%5D/gists{/gist_id}',
            starred_url: 'https://api.github.com/users/github-actions%5Bbot%5D/starred{/owner}{/repo}',
            subscriptions_url: 'https://api.github.com/users/github-actions%5Bbot%5D/subscriptions',
            organizations_url: 'https://api.github.com/users/github-actions%5Bbot%5D/orgs',
            repos_url: 'https://api.github.com/users/github-actions%5Bbot%5D/repos',
            events_url: 'https://api.github.com/users/github-actions%5Bbot%5D/events{/privacy}',
            received_events_url: 'https://api.github.com/users/github-actions%5Bbot%5D/received_events',
            type: 'Bot',
            site_admin: false,
          },
          content_type: 'application/octet-stream',
          state: 'uploaded',
          size: 1787344,
          download_count: 0,
          created_at: '2024-05-16T19:30:26Z',
          updated_at: '2024-05-16T19:30:26Z',
          browser_download_url: 'https://github.com/iot49/leaf/releases/download/v0.0.1/firmware.bin',
        },
        {
          url: 'https://api.github.com/repos/iot49/leaf/releases/assets/168357553',
          id: 168357553,
          node_id: 'RA_kwDOL4ZmU84KCO6x',
          name: 'micropython.bin',
          label: '',
          uploader: {
            login: 'github-actions[bot]',
            id: 41898282,
            node_id: 'MDM6Qm90NDE4OTgyODI=',
            avatar_url: 'https://avatars.githubusercontent.com/in/15368?v=4',
            gravatar_id: '',
            url: 'https://api.github.com/users/github-actions%5Bbot%5D',
            html_url: 'https://github.com/apps/github-actions',
            followers_url: 'https://api.github.com/users/github-actions%5Bbot%5D/followers',
            following_url: 'https://api.github.com/users/github-actions%5Bbot%5D/following{/other_user}',
            gists_url: 'https://api.github.com/users/github-actions%5Bbot%5D/gists{/gist_id}',
            starred_url: 'https://api.github.com/users/github-actions%5Bbot%5D/starred{/owner}{/repo}',
            subscriptions_url: 'https://api.github.com/users/github-actions%5Bbot%5D/subscriptions',
            organizations_url: 'https://api.github.com/users/github-actions%5Bbot%5D/orgs',
            repos_url: 'https://api.github.com/users/github-actions%5Bbot%5D/repos',
            events_url: 'https://api.github.com/users/github-actions%5Bbot%5D/events{/privacy}',
            received_events_url: 'https://api.github.com/users/github-actions%5Bbot%5D/received_events',
            type: 'Bot',
            site_admin: false,
          },
          content_type: 'application/octet-stream',
          state: 'uploaded',
          size: 1721808,
          download_count: 0,
          created_at: '2024-05-16T19:30:26Z',
          updated_at: '2024-05-16T19:30:26Z',
          browser_download_url: 'https://github.com/iot49/leaf/releases/download/v0.0.1/micropython.bin',
        },
      ],
      tarball_url: 'https://api.github.com/repos/iot49/leaf/tarball/v0.0.1',
      zipball_url: 'https://api.github.com/repos/iot49/leaf/zipball/v0.0.1',
      body: '**Full Changelog**: https://github.com/iot49/leaf/commits/v0.0.1',
    },
  ];
}
