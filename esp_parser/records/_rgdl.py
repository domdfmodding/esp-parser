#!/usr/bin/env python3
#
#  _rgdl.py
"""
RGDL record type.
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
from io import BytesIO
from typing import Iterator

# this package
from esp_parser.subrecords import EDID
from esp_parser.types import CStringRecord, FormIDRecord, Record, RecordType, Uint32Record

__all__ = ["RGDL"]


class RGDL(Record):
	"""
	Ragdoll.
	"""

	class NVER(Uint32Record):
		"""
		Version.
		"""

	# class DATA(RecordType):
	# 	"""
	# 	General Data.
	# 	"""

	class XNAM(FormIDRecord):
		"""
		Actor Base.

		Form ID of a :class:`~.CREA` or :class:`~.NPC_` record.
		"""

	class TNAM(FormIDRecord):
		"""
		Body Part Data.

		Form ID of a :class:`~.BPTD` record.
		"""

	# class RAFD(RecordType):
	# 	"""
	# 	Feedback Data.
	# 	"""

	# class RAFB(RecordType):
	# 	"""
	# 	Feedback Dynamic Bones.
	# 	"""

	# class RAPS(RecordType):
	# 	"""
	# 	Pose Matching Data.
	# 	"""

	class ANAM(CStringRecord):
		"""
		Death Pose.
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
			elif record_type in {b"ANAM", b"DATA", b"NVER", b"RAFB", b"RAFD", b"RAPS", b"TNAM", b"XNAM"}:
				yield getattr(cls, record_type.decode()).parse(raw_bytes)
			else:
				raise NotImplementedError(record_type)
