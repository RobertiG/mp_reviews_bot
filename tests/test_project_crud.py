from mp_reviews_bot.projects import service as project_service


def test_project_crud_roundtrip():
    project = project_service.create_project(name="Test Project", owner_id="owner-1")

    assert project.id
    assert project.name == "Test Project"
    assert project.owner_id == "owner-1"

    fetched = project_service.get_project(project.id)
    assert fetched is not None
    assert fetched.id == project.id

    updated = project_service.update_project(project.id, name="Updated Project")
    assert updated.name == "Updated Project"

    deleted = project_service.delete_project(project.id)
    assert deleted is True

    missing = project_service.get_project(project.id)
    assert missing is None
