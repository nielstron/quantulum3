import unittest

from ..classes import Entity, Quantity, Unit


class TestClasses(unittest.TestCase):
    def setUp(self):
        self.e = Entity(name="test_entity", dimensions=list(), uri="test_uri")
        self.u = Unit(
            name="test_unit",
            entity=self.e,
            surfaces=["test_surface"],
            uri="test_uri",
            symbols=["test_symbol"],
        )
        self.q = Quantity(
            1.0,
            self.u,
            surface="test_surface",
            span=(0, 1),
            uncertainty=0.1,
            lang="en_US",
        )

    def test_entity_to_dict(self):
        entity_dict = self.e.to_dict()
        self.assertIsInstance(entity_dict, dict)
        self.assertEqual(entity_dict["name"], self.e.name)
        self.assertEqual(entity_dict["dimensions"], self.e.dimensions)
        self.assertEqual(entity_dict["uri"], self.e.uri)

    def test_entity_to_json(self):
        entity_json = self.e.to_json()
        self.assertIsInstance(entity_json, str)

    def test_entity_from_dict(self):
        entity_dict = self.e.to_dict()
        entity = Entity.from_dict(entity_dict)
        self.assertEqual(entity, self.e)
        self.assertIsInstance(entity, Entity)

    def test_entity_from_json(self):
        entity_json = self.e.to_json()
        entity = Entity.from_json(entity_json)
        self.assertIsInstance(entity, Entity)

    def test_unit_to_dict(self):
        unit_dict = self.u.to_dict()
        self.assertIsInstance(unit_dict, dict)
        self.assertEqual(unit_dict["name"], self.u.name)
        self.assertEqual(unit_dict["entity"], self.u.entity.name)
        self.assertEqual(unit_dict["surfaces"], self.u.surfaces)
        self.assertEqual(unit_dict["uri"], self.u.uri)
        self.assertEqual(unit_dict["symbols"], self.u.symbols)
        self.assertEqual(unit_dict["dimensions"], self.u.dimensions)
        self.assertEqual(unit_dict["currency_code"], self.u.currency_code)
        self.assertEqual(unit_dict["original_dimensions"], self.u.original_dimensions)
        self.assertEqual(unit_dict["lang"], self.u.lang)

    def test_unit_to_json(self):
        unit_json = self.u.to_json()
        self.assertIsInstance(unit_json, str)

    def test_unit_from_dict(self):
        unit_dict = self.u.to_dict(include_entity_dict=True)
        unit = Unit.from_dict(unit_dict)
        self.assertEqual(unit, self.u)
        self.assertIsInstance(unit, Unit)

    def test_unit_from_json(self):
        unit_json = self.u.to_json(include_entity_dict=True)
        unit = Unit.from_json(unit_json)
        self.assertEqual(unit, self.u)
        self.assertIsInstance(unit, Unit)

    def test_quantity_to_dict(self):
        quantity_dict = self.q.to_dict()
        self.assertIsInstance(quantity_dict, dict)
        self.assertEqual(quantity_dict["value"], self.q.value)
        self.assertEqual(quantity_dict["unit"], self.u.name)
        self.assertEqual(quantity_dict["surface"], self.q.surface)
        self.assertEqual(quantity_dict["span"], self.q.span)
        self.assertEqual(quantity_dict["uncertainty"], self.q.uncertainty)
        self.assertEqual(quantity_dict["lang"], self.q.lang)

    def test_quantity_to_json(self):
        quantity_json = self.q.to_json()
        self.assertIsInstance(quantity_json, str)

    def test_quantity_from_dict(self):
        quantity_dict = self.q.to_dict(include_unit_dict=True, include_entity_dict=True)
        quantity = Quantity.from_dict(quantity_dict)
        self.assertEqual(quantity, self.q)
        self.assertIsInstance(quantity, Quantity)

    def test_quantity_from_json(self):
        quantity_json = self.q.to_json(include_unit_dict=True, include_entity_dict=True)
        quantity = Quantity.from_json(quantity_json)
        self.assertEqual(quantity, self.q)
        self.assertIsInstance(quantity, Quantity)
