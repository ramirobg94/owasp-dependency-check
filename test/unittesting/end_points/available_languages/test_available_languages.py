from flask import url_for


def test_available_languages(client):
    res = client.get(url_for(".available_languages"))

    assert res.json == {'languajes': ['nodejs']}
