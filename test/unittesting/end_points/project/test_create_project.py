import json

from flask import url_for


def test_create_project_ok(client):
    path = "lang={lang}&type={type}&repo={repo}".format(
        lang="nodejs",
        repo="https://mycustomrepo.com/user",
        type="git")

    res = client.get("{}?{}".format(url_for(".create"), path))

    assert res.json.get("project", None) is not None
    assert type(res.json["project"]) is int


def test_create_project_invalid_repo(client):
    res = client.get(url_for(".create"))

    assert res.json == {'error': 'Invalid repo value'}


def test_create_project_non_supported_lang(client):
    path = "lang={lang}&type={type}&repo={repo}".format(
        lang="blabla",
        repo="https://mycustomrepo.com/user",
        type="git")

    res = client.get("{}?{}".format(url_for(".create"), path))

    assert res.json == {'error': "Language 'blabla' not available"}