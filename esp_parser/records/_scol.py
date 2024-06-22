#!/usr/bin/env python3
#
#  _scol.py
"""
SCOL record type.
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
from typing import Iterator, List, NamedTuple, Type

# 3rd party
from typing_extensions import Self

# this package
from esp_parser.subrecords import EDID, OBND, Model
from esp_parser.types import FormIDRecord, Record, RecordType
from esp_parser.utils import namedtuple_qualname_repr

__all__ = ["SCOL"]


class SCOL(Record):
	"""
	Static Collection.
	"""

	class ONAM(FormIDRecord):
		"""
		Static.
		"""

	class DataItem(NamedTuple):
		"""
		Placements.
		"""

		xp: float
		yp: float
		zp: float
		xr: float
		yr: float
		zr: float
		scale: float

		@classmethod
		def unpack(cls: Type[Self], raw_bytes: BytesIO) -> Self:
			"""
			Unpack bytes for the :class:`~.SCOL.DataItem`.
			"""

			return cls(*struct.unpack("<fffffff", raw_bytes.read(28)))

		def pack(self) -> bytes:
			"""
			Pack the :class:`~.SCOL.DataItem` to bytes.
			"""

			return struct.pack("<fffffff", *self)

		def __repr__(self) -> str:
			return namedtuple_qualname_repr(self)

	class DATA(List[DataItem], RecordType):
		"""
		Placements.
		"""

		def __repr__(self) -> str:
			return f"{self.__class__.__qualname__}({super().__repr__()})"

		@classmethod
		def parse(cls: Type[Self], raw_bytes: BytesIO) -> Self:
			"""
			Parse this subrecord.

			:param raw_bytes: Raw bytes for this record
			"""

			size = struct.unpack("<H", raw_bytes.read(2))[0]
			count = size // 28
			assert not size % 28
			self = cls()
			for _ in range(count):
				buf = BytesIO(raw_bytes.read(28))
				self.append(SCOL.DataItem.unpack(buf))

			return self

		def unparse(self) -> bytes:
			"""
			Turn this subrecord back into raw bytes for an ESP file.
			"""

			body = b"".join(di.pack() for di in self)
			size = struct.pack("<H", len(body))

			return b"DATA" + size + body

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
			elif record_type == b"ONAM":
				yield cls.ONAM.parse(raw_bytes)
			elif record_type == b"DATA":
				yield cls.DATA.parse(raw_bytes)
			elif record_type in Model.members:
				yield Model.parse_member(record_type, raw_bytes)
			else:
				raise NotImplementedError(record_type)