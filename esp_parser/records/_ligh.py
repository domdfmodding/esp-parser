#!/usr/bin/env python3
#
#  _ligh.py
"""
LIGH record type.
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
from typing import Iterator, Type

# 3rd party
import attrs
from typing_extensions import Self

# this package
from esp_parser.subrecords import EDID, OBND, Model
from esp_parser.types import CStringRecord, Float32Record, FormIDRecord, Record, RecordType

__all__ = ["LIGH"]


class LIGH(Record):
	"""
	Light.
	"""

	class SCRI(FormIDRecord):
		"""
		Form ID of a :class:`~.SCPT` record.
		"""

	class FULL(CStringRecord):
		"""
		Name.
		"""

	class ICON(CStringRecord):
		"""
		Large icon filename.
		"""

	class MICO(CStringRecord):
		"""
		Small icon filename.
		"""

	@attrs.define
	class DATA(RecordType):
		"""
		Data.
		"""

		time: int
		radius: int
		#: 4 bytes of RGBA
		color: bytes
		flags: int  # See https://tes5edit.github.io/fopdoc/Fallout3/Records/LIGH.html
		falloff_exponent: float
		fov: float
		value: int
		weight: float

		@classmethod
		def parse(cls: Type[Self], raw_bytes: BytesIO) -> Self:
			"""
			Parse this subrecord.

			:param raw_bytes: Raw bytes for this record
			"""

			assert raw_bytes.read(2) == b"\x20\x00"
			return cls(*struct.unpack("<iI4sIffIf", raw_bytes.read(32)))

		def unparse(self) -> bytes:
			"""
			Turn this subrecord back into raw bytes for an ESP file.
			"""
			packed = struct.pack(
					"<iI4sIffIf",
					self.time,
					self.radius,
					self.color,
					self.flags,
					self.falloff_exponent,
					self.fov,
					self.value,
					self.weight,
					)
			return b"DATA" + b"\x20\x00" + packed

	class FNAM(Float32Record):
		"""
		Fade value.
		"""

	class SNAM(FormIDRecord):
		"""
		Sound.

		Form ID of a :class:`~.SOUN` record.
		"""

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
				yield EDID.parse(raw_bytes)
			elif record_type == b"OBND":
				yield OBND.parse(raw_bytes)
			elif record_type in {b"SCRI", b"FULL", b"ICON", b"MICO", b"DATA", b"FNAM", b"SNAM"}:
				yield getattr(cls, record_type.decode()).parse(raw_bytes)
			elif record_type in Model.members:
				yield Model.parse_member(record_type, raw_bytes)
			else:
				raise NotImplementedError(record_type)
