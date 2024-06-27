#!/usr/bin/env python3
#
#  _arma.py
"""
ARMA record type.
"""
#
#  Copyright © 2024 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
import struct
from io import BytesIO
from typing import Iterator, Tuple, Type

# 3rd party
import attrs
from typing_extensions import Self

# this package
from esp_parser import subrecords
from esp_parser.types import CStringRecord, Int32Record, Record, RecordType, StructRecord

__all__ = ["ARMA"]


class ARMA(Record):
	"""
	Armor Addon.
	"""

	class FULL(CStringRecord):
		"""
		Name.
		"""

	class ICON(CStringRecord):
		"""
		Male inventory icon filename.
		"""

	class MICO(CStringRecord):
		"""
		Male message icon filename.
		"""

	class ICO2(CStringRecord):
		"""
		Female inventory icon filename.
		"""

	class MIC2(CStringRecord):
		"""
		Female message icon filename.
		"""

	class ETYP(Int32Record):
		"""
		Equipment Type.

		https://tes5edit.github.io/fopdoc/FalloutNV/Records/Subrecords/ETYP.html
		"""

	@attrs.define
	class DATA(StructRecord):
		"""
		Data.
		"""

		value: int
		max_condition: int
		weight: float

		@staticmethod
		def get_struct_and_size() -> Tuple[str, int]:
			"""
			Returns the pack/unpack struct string and the corresponding size.
			"""

			return "<IIf", 12

		@staticmethod
		def get_field_names() -> Tuple[str, ...]:
			"""
			Returns a list of attributes on this class in the order they should be packed.
			"""

			return ("value", "max_condition", "weight")

	@attrs.define
	class DNAM(StructRecord):  # noqa: D106  # TODO

		#: Value is divided by 100.
		ar: int
		flags: int  # See https://tes5edit.github.io/fopdoc/FalloutNV/Records/ARMO.html
		unknown: bytes

		@staticmethod
		def get_struct_and_size() -> Tuple[str, int]:
			"""
			Returns the pack/unpack struct string and the corresponding size.
			"""

			return "<hH8s", 12

		@staticmethod
		def get_field_names() -> Tuple[str, ...]:
			"""
			Returns a list of attributes on this class in the order they should be packed.
			"""

			return ("ar", "flags", "unknown")

		@classmethod
		def parse(cls: Type[Self], raw_bytes: BytesIO) -> RecordType:  # type: ignore[override]
			"""
			Parse this subrecord.

			:param raw_bytes: Raw bytes for this record
			"""

			unpack_struct, expected_size = cls.get_struct_and_size()
			size = struct.unpack("<H", raw_bytes.read(2))[0]
			if size == 4:
				# Fallout 3
				buf = BytesIO(struct.pack("<H", 4) + raw_bytes.read(4))
				return subrecords.DNAM.parse(buf)
			else:
				if size != expected_size:
					raise ValueError(f"Size mismatch for {cls}: Expected {expected_size}, got {size}")
				return cls(*struct.unpack(unpack_struct, raw_bytes.read(size)))

	@classmethod
	def parse_subrecords(cls, raw_bytes: BytesIO) -> Iterator[RecordType]:
		"""
		Parse this record's subrecords.

		:param raw_bytes: Raw bytes for this record's subrecords
		"""

		while True:
			record_type = raw_bytes.read(4)
			if not record_type:
				break

			if record_type == b"EDID":
				yield subrecords.EDID.parse(raw_bytes)
			elif record_type == b"OBND":
				yield subrecords.OBND.parse(raw_bytes)
			elif record_type == b"BMDT":
				yield subrecords.BMDT.parse(raw_bytes)
			elif record_type in {b"BMDT", b"DATA", b"DNAM", b"ETYP", b"FULL", b"ICO2", b"ICON", b"MIC2", b"MICO"}:
				yield getattr(cls, record_type.decode()).parse(raw_bytes)
			elif record_type in subrecords.Model.members:
				yield subrecords.Model.parse_member(record_type, raw_bytes)
			else:
				raise NotImplementedError(record_type)
