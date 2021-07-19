from labelbox.data.annotation_types.data.raster import RasterData
from labelbox.data.annotation_types.ner import TextEntity
from labelbox.data.annotation_types.geometry.rectangle import Rectangle
from labelbox.data.annotation_types.geometry.polygon import Polygon
from labelbox.data.annotation_types.geometry.line import Line
from labelbox.data.annotation_types.geometry.point import Point
from labelbox.data.annotation_types.geometry.mask import Mask

from labelbox.data.annotation_types.annotation import AnnotationType, ObjectAnnotation
from labelbox.data.serialization.ndjson.classifications import NDClassification, NDSubclassification, NDSubclassificationType
from labelbox.data.serialization.ndjson.base import DataRow, NDAnnotation
from uuid import UUID, uuid4
from pydantic import BaseModel, validator
from typing import List, Tuple, Union


class NDObject(NDAnnotation):
    classifications: List[NDSubclassificationType] = []


class _Point(BaseModel):
    x: float
    y: float


class Bbox(BaseModel):
    top: float
    left: float
    height: float
    width: float


class NDPoint(NDObject):
    point: _Point

    def to_common(self):
        return Point(x=self.point.x, y=self.point.y)

    @classmethod
    def from_common(cls, annotation, data):
        return cls(point={
            'x': annotation.value.x,
            'y': annotation.value.y
        },
                   dataRow=DataRow(id=data.uid),
                   schemaId=annotation.schema_id,
                   uuid=annotation.extra.get('uuid'),
                   classifications=[
                       NDSubclassification.from_common(annot)
                       for annot in annotation.classifications
                   ])


class NDLine(NDObject):
    line: List[_Point]

    def to_common(self):
        return Line(points=[Point(x=pt.x, y=pt.y) for pt in self.line])

    @classmethod
    def from_common(cls, annotation, data):
        return cls(line=[{
            'x': pt.x,
            'y': pt.y
        } for pt in annotation.value.points],
                   dataRow=DataRow(id=data.uid),
                   schemaId=annotation.schema_id,
                   uuid=annotation.extra.get('uuid'),
                   classifications=[
                       NDSubclassification.from_common(annot)
                       for annot in annotation.classifications
                   ])


class NDPolygon(NDObject):
    polygon: List[_Point]

    def to_common(self):
        return Polygon(points=[Point(x=pt.x, y=pt.y) for pt in self.polygon])

    @classmethod
    def from_common(cls, annotation, data):
        return cls(polygon=[{
            'x': pt.x,
            'y': pt.y
        } for pt in annotation.value.points],
                   dataRow=DataRow(id=data.uid),
                   schemaId=annotation.schema_id,
                   uuid=annotation.extra.get('uuid'),
                   classifications=[
                       NDSubclassification.from_common(annot)
                       for annot in annotation.classifications
                   ])


class NDRectangle(NDObject):
    bbox: Bbox

    def to_common(self):
        return Rectangle(start=Point(x=self.bbox.left, y=self.bbox.top),
                         end=Point(x=self.bbox.left + self.bbox.width,
                                   y=self.bbox.top + self.bbox.height))

    @classmethod
    def from_common(cls, annotation, data):
        return cls(bbox=Bbox(
            top=annotation.value.start.y,
            left=annotation.value.start.x,
            height=annotation.value.end.y - annotation.value.start.y,
            width=annotation.value.end.x - annotation.value.start.x),
                   dataRow=DataRow(id=data.uid),
                   schemaId=annotation.schema_id,
                   uuid=annotation.extra.get('uuid'),
                   classifications=[
                       NDSubclassification.from_common(annot)
                       for annot in annotation.classifications
                   ])


class _Mask(BaseModel):
    instanceURI: str
    colorRGB: Tuple[int, int, int]


class NDMask(NDObject):
    mask: _Mask

    def to_common(self):
        return Mask(mask=RasterData(url=self.mask.instanceURI),
                    color_rgb=self.mask.colorRGB)

    @classmethod
    def from_common(cls, annotation, data):
        return cls(mask=_Mask(instanceURI=annotation.value.mask.url,
                              colorRGB=annotation.value.color_rgb),
                   dataRow=DataRow(id=data.uid),
                   schemaId=annotation.schema_id,
                   uuid=annotation.extra.get('uuid'),
                   classifications=[
                       NDSubclassification.from_common(annot)
                       for annot in annotation.classifications
                   ])


class Location(BaseModel):
    start: int
    end: int


class NDTextEntity(NDObject):
    location: Location

    def to_common(self):
        return TextEntity(start=self.location.start, end=self.location.end)

    @classmethod
    def from_common(cls, annotation, data):
        return cls(location=Location(
            start=annotation.value.start,
            end=annotation.value.end,
        ),
                   dataRow=DataRow(id=data.uid),
                   schemaId=annotation.schema_id,
                   uuid=annotation.extra.get('uuid'),
                   classifications=[
                       NDSubclassification.from_common(annot)
                       for annot in annotation.classifications
                   ])


class NDObject:

    @classmethod
    def from_common(cls, annotation, data):
        obj = cls.lookup_object(annotation)
        if obj is None:
            raise TypeError(
                f"Unable to convert object to MAL format. `{type(annotation.value)}`"
            )
        return obj.from_common(annotation, data)

    @staticmethod
    def to_common(annotation):
        common_annotation = annotation.to_common()
        classifications = [
            NDSubclassification.to_common(annot)
            for annot in annotation.classifications
        ]
        return ObjectAnnotation(value=common_annotation,
                                schema_id=annotation.schemaId,
                                classifications=classifications,
                                extra={'uuid': annotation.uuid})

    @staticmethod
    def lookup_object(annotation: AnnotationType):
        return {
            Line: NDLine,
            Point: NDPoint,
            Polygon: NDPolygon,
            Rectangle: NDRectangle,
            Mask: NDMask,
            TextEntity: NDTextEntity
        }.get(type(annotation.value))


NDObjectType = Union[Bbox, NDLine, NDPolygon, NDPoint, NDRectangle, NDMask,
                     NDTextEntity]
