from pydantic import ValidationError
import pytest
import cv2

from labelbox.data.annotation_types.geometry import Point


def test_point():
    with pytest.raises(ValidationError):
        line = Point()

    with pytest.raises(TypeError):
        line = Point([0, 1])

    point = Point(x=0, y=1)
    expected = {"coordinates": [0, 1], "type": "Point"}
    assert point.geometry == expected
    expected['coordinates'] = tuple(expected['coordinates'])
    assert point.shapely.__geo_interface__ == expected

    raster = point.raster(height=32, width=32)
    assert (cv2.imread("tests/data/assets/point.png")[:, :, 0] == raster).all()