from httpx import AsyncClient
from tests.util import is_subset


async def test_modify_tree(create_trees, async_client: AsyncClient):
    tree = create_trees[0]
    new_title = "New Title"
    response = await async_client.put(f"/api/tree/{tree['uuid']}", json={"title": new_title})
    assert response.status_code == 200
    response = response.json()
    assert response["title"] == new_title
    del response["updated_at"]
    del response["title"]
    assert is_subset(response, tree)


async def test_modify_branch(create_trees, async_client: AsyncClient):
    tree = create_trees[1]
    branch = tree["branches"][1]
    new_desc = "new_desc"
    response = await async_client.put(f"/api/branch/{branch['uuid']}", json={"description": new_desc})
    assert response.status_code == 200
    response = response.json()
    assert response["description"] == new_desc
    del response["updated_at"]
    del response["description"]
    assert is_subset(response, branch)


async def test_delete_tree(create_trees, async_client: AsyncClient):
    branch_count = (await async_client.get("/api/branch/count")).json()
    tree = create_trees[0]
    response = await async_client.delete(f"/api/tree/{tree['uuid']}")
    assert response.status_code == 200
    response = await async_client.get(f"/api/tree/{tree['uuid']}")
    assert response.status_code == 404
    # verify the branches are gone, too
    assert (await async_client.get("/api/branch/count")).json() == branch_count - len(tree["branches"])
