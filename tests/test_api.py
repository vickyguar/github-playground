import httpx
import pytest

from argentina_data_lab.api import ArgentinaDataClient


def mock_client(handler) -> ArgentinaDataClient:
    return ArgentinaDataClient(client=httpx.Client(transport=httpx.MockTransport(handler)))


def test_search_series_calls_official_search_endpoint() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/search")
        assert request.url.params["query"] == "inflación"
        assert request.url.params["limit"] == "2"
        return httpx.Response(200, json={"data": [], "count": 0})

    with mock_client(handler) as client:
        assert client.search_series("inflación", limit=2)["count"] == 0


def test_fetch_series_parses_observation_csv() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/series")
        assert request.url.params["ids"] == "series.one,series.two"
        assert request.url.params["start_date"] == "2020-01-01"
        return httpx.Response(
            200,
            text="indice_tiempo,series_one,series_two\n2020-01-01,1.5,2.5\n",
        )

    with mock_client(handler) as client:
        frame = client.fetch_series(
            ["series.one", "series.two"],
            start_date="2020-01-01",
        )

    assert list(frame.columns) == ["indice_tiempo", "series_one", "series_two"]
    assert frame.loc[0, "series_one"] == 1.5


def test_list_provinces_reads_georef_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/provincias")
        return httpx.Response(
            200,
            json={"provincias": [{"id": "02", "nombre": "Ciudad Autónoma de Buenos Aires"}]},
        )

    with mock_client(handler) as client:
        provinces = client.list_provinces()

    assert provinces[0]["id"] == "02"


def test_search_series_rejects_empty_query() -> None:
    with mock_client(lambda _: httpx.Response(200, json={"data": []})) as client:
        with pytest.raises(ValueError, match="cannot be empty"):
            client.search_series(" ")
