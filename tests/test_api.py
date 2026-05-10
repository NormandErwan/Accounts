from unittest.mock import MagicMock, patch

import httpx
import pytest

from enrich_csv.api import search_company


def _mock_response(results: list) -> MagicMock:
    resp = MagicMock()
    resp.json.return_value = {"results": results}
    return resp


def _hit(name: str = "Test SA", naf: str = "47.11", siren: str = "123456789") -> dict:
    return {"nom_complet": name, "siren": siren, "siege": {"activite_principale": naf}}


def test_search_company_returns_parsed_result():
    with patch("httpx.get", return_value=_mock_response([_hit()])):
        result = search_company("test")
    assert result == {"name": "Test SA", "naf": "47.11", "siren": "123456789"}


def test_search_company_returns_none_on_empty_results():
    with patch("httpx.get", return_value=_mock_response([])):
        result = search_company("unknown")
    assert result is None


def test_search_company_returns_none_on_http_status_error():
    err = httpx.HTTPStatusError("404", request=MagicMock(), response=MagicMock())
    with patch("httpx.get", side_effect=err):
        assert search_company("test") is None


def test_search_company_returns_none_on_timeout():
    with patch("httpx.get", side_effect=httpx.TimeoutException("timeout")):
        assert search_company("test") is None


def test_search_company_returns_none_on_connection_error():
    with patch("httpx.get", side_effect=httpx.ConnectError("refused")):
        assert search_company("test") is None


def test_search_company_returns_none_on_json_decode_error():
    resp = MagicMock()
    resp.json.side_effect = ValueError("bad json")
    with patch("httpx.get", return_value=resp):
        assert search_company("test") is None


def test_search_company_does_not_swallow_keyboard_interrupt():
    with pytest.raises(KeyboardInterrupt), patch("httpx.get", side_effect=KeyboardInterrupt):
        search_company("test")


def test_search_company_handles_missing_siege_key():
    hit = {"nom_complet": "Test", "siren": "123", "siege": {}}
    with patch("httpx.get", return_value=_mock_response([hit])):
        result = search_company("test")
    assert result is not None
    assert result["naf"] == ""
