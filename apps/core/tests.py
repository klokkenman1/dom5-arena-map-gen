import copy
from unittest import mock

from django.urls import reverse

import pytest

from apps.core.factories import NationFactory, UnitFactory
from apps.core.serializers import (
    GenerateMapSerializer,
    NationSerializer,
    UnitSerializer,
)
from apps.domdata.models import Nation, Unit

pytestmark = pytest.mark.django_db()


@pytest.fixture
def prepare_data():
    NationFactory.create_batch(10, **{"modded": 1})
    NationFactory.create_batch(10, **{"modded": 2})
    NationFactory.create_batch(10, **{"modded": 3})
    UnitFactory.create_batch(10, **{"modded": 1})
    UnitFactory.create_batch(10, **{"modded": 2})
    UnitFactory.create_batch(10, **{"modded": 3})


@pytest.mark.parametrize("test_input,expected", [("1", 10), ("1,2", 20), ("1,2,3", 30)])
def test_autocomplete_units_no_search_modded(
    prepare_data, client, test_input, expected
):
    url = reverse("v0:autocomplete_units_view") + f"?modded={test_input}"
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.data) == expected


def test_autocomplete_units_no_search_no_modded(prepare_data, client):
    url = reverse("v0:autocomplete_units_view")
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 10


@pytest.mark.parametrize("test_input,expected", [("1", 10), ("1,2", 20), ("1,2,3", 30)])
def test_autocomplete_nations_no_search_modded(
    prepare_data, client, test_input, expected
):
    url = reverse("v0:autocomplete_nations_view") + f"?modded={test_input}"
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.data) == expected


def test_autocomplete_nations_no_search_no_modded(prepare_data, client):
    url = reverse("v0:autocomplete_nations_view")
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 10


def test_autocomplete_units_search_by_dominion_id(prepare_data, client):
    latest_unit = Unit.objects.filter(modded=Unit.VANILLA).last()
    url = reverse("v0:autocomplete_units_view") + f"?search={latest_unit.dominion_id}"
    response = client.get(url)
    assert response.status_code == 200
    assert response.data[0] == UnitSerializer(latest_unit).data


def test_autocomplete_units_search_by_name(prepare_data, client):
    latest_unit = Unit.objects.filter(modded=Unit.VANILLA).last()
    url = reverse("v0:autocomplete_units_view") + f"?search={latest_unit.name}"
    response = client.get(url)
    assert response.status_code == 200
    assert response.data[0] == UnitSerializer(latest_unit).data


def test_autocomplete_units_search_by_partial_name(prepare_data, client):
    latest_unit = Unit.objects.filter(modded=Unit.VANILLA).last()
    url = reverse("v0:autocomplete_units_view") + f"?search={latest_unit.name[:1]}"
    response = client.get(url)
    assert response.status_code == 200
    assert any([obj == UnitSerializer(latest_unit).data for obj in response.data])


def test_autocomplete_nations_search_by_dominion_id(prepare_data, client):
    nation = Nation.objects.filter(modded=Nation.VANILLA).last()
    url = reverse("v0:autocomplete_nations_view") + f"?search={nation.dominion_id}"
    response = client.get(url)
    assert response.status_code == 200
    assert response.data[0] == NationSerializer(nation).data


def test_autocomplete_nations_search_by_name(prepare_data, client):
    nation = Nation.objects.filter(modded=Nation.VANILLA).last()
    url = reverse("v0:autocomplete_nations_view") + f"?search={nation.name}"
    response = client.get(url)
    assert response.status_code == 200
    assert response.data[0] == NationSerializer(nation).data


def test_autocomplete_nations_search_by_partial_name(prepare_data, client):
    nation = Nation.objects.filter(modded=Nation.VANILLA).last()
    url = reverse("v0:autocomplete_nations_view") + f"?search={nation.name[:1]}"
    response = client.get(url)
    assert response.status_code == 200
    assert any([obj == NationSerializer(nation).data for obj in response.data])


@pytest.fixture
def data_for_mapgen():
    nation1 = NationFactory(era=1, name="Tir na n'Og", dominion_id=1)
    nation2 = NationFactory(era=1, name="T'ien Ch'i", dominion_id=2)
    UnitFactory(dominion_id=1786)
    UnitFactory(dominion_id=7)
    UnitFactory(dominion_id=105)
    UnitFactory(dominion_id=408)
    return (
        {
            "land_nation_1": "(EA) Tir na n'Og",
            "land_nation_2": "(EA) T'ien Ch'i",
            "water_nation_1": "",
            "water_nation_2": "",
            "commanders": [
                {
                    "dominion_id": "1786",
                    "name": "Fir Bolg",
                    "id": "6a10c26a-96dc-49c4-9663-75151a3a609a",
                    "for_nation": "(EA) Tir na n'Og",
                    "quantity": 1,
                    "magic": {"fire": "2", "blood": "2"},
                },
                {
                    "dominion_id": "7",
                    "name": "Emerald Guard",
                    "id": "02d84d0c-1cbd-41ed-98a6-b5949010155d",
                    "for_nation": "(EA) T'ien Ch'i",
                    "quantity": 1,
                },
            ],
            "units": [
                {
                    "dominion_id": "105",
                    "name": "Woodhenge Druid",
                    "id": "dc5e61de-3747-46b0-bd33-b361cedc78d9",
                    "for_nation": "(EA) Tir na n'Og",
                    "quantity": "10",
                },
                {
                    "dominion_id": "408",
                    "name": "Water Elemental",
                    "id": "23925abc-40c0-4feb-9dcd-4b13d4d336a5",
                    "for_nation": "(EA) T'ien Ch'i",
                    "quantity": "10",
                },
            ],
        },
        nation1,
        nation2,
    )


def test_generate_map_serializer(data_for_mapgen):
    data, nation1, nation2 = data_for_mapgen
    serializer = GenerateMapSerializer(data=data)
    assert serializer.is_valid()
    assert (
        serializer.validated_data["land_nation_1"]
        == f"({nation1.get_era_display()}) {nation1.name}"
    )
    assert (
        serializer.validated_data["land_nation_2"]
        == f"({nation2.get_era_display()}) {nation2.name}"
    )


def test_generate_map_serializer_invalid_nation(data_for_mapgen):
    data, nation1, nation2 = data_for_mapgen
    nation1.delete()
    serializer = GenerateMapSerializer(data=data)
    assert not serializer.is_valid()


def test_generate_map_serializer_invalid_unit(data_for_mapgen):
    data, *c = data_for_mapgen
    Unit.objects.filter(dominion_id=1786).delete()
    serializer = GenerateMapSerializer(data=data)
    assert not serializer.is_valid()


def test_generate_map_serializer_processed_data(data_for_mapgen):
    data, nation1, nation2 = data_for_mapgen
    serializer = GenerateMapSerializer(data=data)
    assert serializer.is_valid()
    returned_data = serializer.process_data(serializer.validated_data)
    assert returned_data == [
        {
            nation1.dominion_id: [
                {
                    "1786": {
                        "magic": {"mag_fire": "2", "mag_blood": "2"},
                        "units": [("105", "10")],
                    }
                }
            ],
            "land_type": "land",
        },
        {nation2.dominion_id: [{"7": {"units": [("408", "10")]}}], "land_type": "land"},
    ]


def test_mapgenerator_function(data_for_mapgen):
    data, nation1, nation2 = data_for_mapgen
    serializer = GenerateMapSerializer(data=data)
    start1, start2 = GenerateMapSerializer.LAND_STARTS
    assert serializer.is_valid()
    returned_data = serializer.process_data(serializer.validated_data)
    mapgenerated_text = serializer.data_into_map(returned_data)
    assert len(mapgenerated_text) == 2
    assert mapgenerated_text[0] == (
        (
            "\n#allowedplayer {0}\n#specstart {0} {1}\n#setland {1}\n#commander 1786\n"
            "#units 10 105\n#clearmagic\n#mag_fire 2\n#mag_blood 2"
        ).format(nation1.dominion_id, start1)
    )
    assert mapgenerated_text[1] == (
        (
            "\n#allowedplayer {0}\n#specstart {0} {1}\n#setland {1}"
            "\n#commander 7\n#units 10 408"
        ).format(nation2.dominion_id, start2)
    )


@pytest.fixture
def data_for_mapgen_uw():
    nation3 = NationFactory(era=1, name="Oceania", dominion_id=3)
    nation4 = NationFactory(era=1, name="Atlantis", dominion_id=4)
    UnitFactory(dominion_id=1786)
    UnitFactory(dominion_id=7)
    UnitFactory(dominion_id=105)
    UnitFactory(dominion_id=408)
    return (
        {
            "land_nation_1": "",
            "land_nation_2": "",
            "water_nation_1": "(EA) Oceania",
            "water_nation_2": "(EA) Atlantis",
            "commanders": [
                {
                    "dominion_id": "7",
                    "name": "Emerald Guard",
                    "id": "02d84d0c-1cbd-41ed-98a6-b5949010155d",
                    "for_nation": "(EA) Oceania",
                    "quantity": "1",
                },
                {
                    "dominion_id": "7",
                    "name": "Emerald Guard",
                    "id": "02d84d0c-1cbd-41ed-98a6-b5949010155d",
                    "for_nation": "(EA) Atlantis",
                    "quantity": "1",
                },
            ],
            "units": [
                {
                    "dominion_id": "408",
                    "name": "Water Elemental",
                    "id": "23925abc-40c0-4feb-9dcd-4b13d4d336a5",
                    "for_nation": "(EA) Oceania",
                    "quantity": "10",
                },
                {
                    "dominion_id": "408",
                    "name": "Water Elemental",
                    "id": "23925abc-40c0-4feb-9dcd-4b13d4d336a5",
                    "for_nation": "(EA) Atlantis",
                    "quantity": "10",
                },
            ],
        },
        nation3,
        nation4,
    )


def test_generate_map_serializer_processed_data_with_water_nation(data_for_mapgen_uw):
    data, nation3, nation4 = data_for_mapgen_uw
    serializer = GenerateMapSerializer(data=data)
    assert serializer.is_valid()
    returned_data = serializer.process_data(serializer.validated_data)
    assert returned_data == [
        {
            nation3.dominion_id: [{"7": {"units": [("408", "10")]}}],
            "land_type": "water",
        },
        {
            nation4.dominion_id: [{"7": {"units": [("408", "10")]}}],
            "land_type": "water",
        },
    ]


def test_mapgenerator_function_with_water_nation(data_for_mapgen_uw):
    data, nation3, nation4 = data_for_mapgen_uw
    serializer = GenerateMapSerializer(data=data)
    start1, start2 = GenerateMapSerializer.WATER_STARTS
    assert serializer.is_valid()
    returned_data = serializer.process_data(serializer.validated_data)
    mapgenerated_text = serializer.data_into_map(returned_data)
    assert len(mapgenerated_text) == 2
    assert mapgenerated_text[0] == (
        (
            "\n#allowedplayer {0}\n#specstart {0} {1}\n#setland {1}"
            "\n#commander 7\n#units 10 408"
        ).format(nation3.dominion_id, start1)
    )
    assert mapgenerated_text[1] == (
        (
            "\n#allowedplayer {0}\n#specstart {0} {1}\n#setland {1}"
            "\n#commander 7\n#units 10 408"
        ).format(nation4.dominion_id, start2)
    )


def test_insert_data_into_template(data_for_mapgen):
    data, *other = data_for_mapgen
    serializer = GenerateMapSerializer(data=data)
    assert serializer.is_valid()
    returned_data = serializer.process_data(serializer.validated_data)
    mapgenerated_text = serializer.data_into_map(returned_data)
    final_map = serializer.substitute(mapgenerated_text)
    assert mapgenerated_text[0] in final_map
    assert mapgenerated_text[1] in final_map
    assert "$nation3" not in final_map
    assert "$nation4" not in final_map


def test_insert_uw_data_into_template(data_for_mapgen_uw):
    data, nation1, nation2 = data_for_mapgen_uw
    serializer = GenerateMapSerializer(data=data)
    assert serializer.is_valid()
    returned_data = serializer.process_data(serializer.validated_data)
    mapgenerated_text = serializer.data_into_map(returned_data)
    final_map = serializer.substitute(mapgenerated_text)
    assert mapgenerated_text[0] in final_map
    assert mapgenerated_text[1] in final_map
    assert "$nation3" not in final_map
    assert "$nation4" not in final_map


def test_map_with_cave(data_for_mapgen):
    data, *other = data_for_mapgen
    data_with_cave = copy.deepcopy(data)
    data_with_cave["use_cave_map"] = True
    serializer = GenerateMapSerializer(data=data_with_cave)
    assert serializer.is_valid()
    returned_data = serializer.process_data(serializer.validated_data)
    mapgenerated_text = serializer.data_into_map(returned_data)
    mocked_open_function = mock.mock_open(read_data="")
    with mock.patch("apps.core.serializers.open", mocked_open_function) as mocked:
        serializer.substitute(mapgenerated_text)
        mocked.assert_called_once_with("apps/core/data/Arena_with_cave.map", "r")


def test_final_view(data_for_mapgen, client):
    data, nation1, nation2 = data_for_mapgen
    serializer = GenerateMapSerializer(data=data)
    url = reverse("v0:generate_map")
    response = client.post(url, data, content_type="application/json")
    assert response.status_code == 200
    assert serializer.is_valid()
    returned_data = serializer.process_data(serializer.validated_data)
    mapgenerated_text = serializer.data_into_map(returned_data)
    final_map = response.data
    assert nation1.name in final_map
    assert nation2.name in final_map
    assert "vs" in final_map
    assert mapgenerated_text[0] in final_map
    assert mapgenerated_text[1] in final_map
    assert "$nation3" not in final_map
    assert "$nation4" not in final_map
