import pytest
from httpx import AsyncClient

from tests.conftest import auth_header, create_test_user, login_user

#If in /api/posts is empty
@pytest.mark.anyio
async def test_get_posts_empty(client: AsyncClient):
    response = await client.get("/api/posts") #get "api/posts" with client.get

    assert response.status_code == 200
    data = response.json()
    assert data["posts"] == [] #posts have to ==[]
    assert data["total"] == 0 #we don't have any post so "total" have to zero
    assert data["has_more"] is False

@pytest.mark.anyio
async def test_get_not_found_posts(client: AsyncClient):
    response = await client.get("/api/posts/1234") #get "api/posts/1234" with client.get

    assert response.status_code == 404
    assert response.json()["detail"] == "Böyle bir post yok"



@pytest.mark.anyio
async def test_create_post_success(client: AsyncClient):
    user = await create_test_user(client) #take the user
    token = await login_user(client)
    headers = auth_header(token)

    response = await client.post(
        "/api/posts",
        json={"title": "First Post", "content": "Content"},
        headers=headers,
    )

    assert response.status_code == 201 # if post is successfully creat
    data = response.json()
    assert data["title"] == "First Post" #check the title
    assert data["content"] == "Content" # check the content
    assert data["user_id"] == user["id"] #check the id with currentUser_id
    assert "id" in data
    assert "date_posted" in data
    assert data["author"]["username"] == "testuser"


#if user create a post , we are checking the authorized
@pytest.mark.anyio
async def test_create_post_unauthorized(client: AsyncClient):
    response = await client.post(
        "/api/posts",
        json={"title": "Test Post", "content": "Test content"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


#Update the Post Successfully
@pytest.mark.anyio
async def test_update_post_success(client: AsyncClient):

    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    #firstly created new post
    response = await client.post(
        "/api/posts",
        json={"title": "Title", "content": "content"},
        headers=headers,
    )
    #take the post_id
    post_id = response.json()["id"]

    #Patch the post
    response = await client.patch(
        f"/api/posts/{post_id}",
        json={"title": "New Title"}, # we want to change only title
        headers=headers,
    )
    #if status code ==200
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["content"] == "content"


#if a users wants to change a posts that doesn't belong to user's
@pytest.mark.anyio
async def test_update_post_wrong_user(client: AsyncClient):
    await create_test_user(client, username="user1", email="user1@example.com")#created  user 1
    token1 = await login_user(client, email="user1@example.com")# take user1's token

    #create a new post for User1
    response = await client.post(
        "/api/posts",
        json={"title": "This Post for User1", "content": "User1 can be edit this post"},
        headers=auth_header(token1),
    )
    post_id = response.json()["id"]# take the post_id

    await create_test_user(client, username="user2", email="user2@example.com")#created user2
    token2 = await login_user(client, email="user2@example.com")# take user2's token

    #We want to patch this post but with user2
    response = await client.patch(
        f"/api/posts/{post_id}",
        json={"title": "Hacked Title"},
        headers=auth_header(token2),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Yetkili kişi değil"


## Test Pagination
@pytest.mark.anyio
async def test_get_posts_with_pagination(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    #We are creating 5 posts
    for i in range(5):
        response = await client.post(
            "/api/posts",
            json={"title": f"Post {i}", "content": f"Content for post {i}"},
            headers=headers,
        )
        assert response.status_code == 201 #check the created

    # if we don't denote  the limit
    response = await client.get("/api/posts")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5 #total posts
    assert len(data["posts"]) == 5 #in the page posts
    assert data["has_more"] is False # false because we see all posts

    #if we denote the limit ,ex:2
    response = await client.get("/api/posts?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5 #total posts
    assert len(data["posts"]) == 2 #in the page posts
    assert data["has_more"] is True #true because we don't see all posts

    #if we denote limit and skip, skip 2 posts and return the next 2 posts
    response = await client.get("/api/posts?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["posts"]) == 2
    assert data["skip"] == 2
    assert data["limit"] == 2
