from flask import url_for


def test_home_ok(client):
    res = client.get(url_for(".home"))

    assert res.data == b"""
    <html><head><title>Security Dependency Checker</title></head><body>
    <h1>Wellcome to the Security Dependency Checker</h1>
    <p>To access to interactive use of SDC API you can follow this link: <a href="/apidocs/index.html">Access to API &rarr;</a></p>
    </body></html>
    """
