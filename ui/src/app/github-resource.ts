import { github_owner, github_repo } from "./env";
import { FetchError } from "./errors";

export async function get_resource(
  resource: string = "releases",
): Promise<any> {
  const response = await fetch(
    `https://api.github.com/repos/${github_owner}/${github_repo}/${resource}`,
    {
      headers: {
        Accept: "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        //"Authorization:": `Bearer ${github_token}`,
      },
    },
  );
  console.log(response);
  if (!response.ok) {
    throw new FetchError(
      `Failed downloading ${github_owner}/${github_repo}/${resource}, status: ${response.status}`,
    );
  }
  return await response.json();
}

export async function get_asset(
  release: any,
  tag_name: string,
  asset_name: string = "firmware.bin",
): Promise<any> {
  if (release.tag_name === tag_name) {
    for (const asset of release.assets) {
      if (asset.name === asset_name) {
        return await get_resource(`releases/assets/${asset.id}`);
      }
    }
  }
}
