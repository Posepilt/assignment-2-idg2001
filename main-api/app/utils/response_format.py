"""Helper for returning responses in different formats (JSON, XML, CSV)."""

import csv
import io
from fastapi.responses import JSONResponse, Response
from dicttoxml import dicttoxml


def format_response(data, fmt="json"):
    """Return data in the requested format."""
    fmt = fmt.lower()

    if fmt == "xml":
        xml_bytes = dicttoxml(data, custom_root="result", attr_type=False)
        return Response(content=xml_bytes, media_type="application/xml")

    elif fmt == "csv":
        if isinstance(data, dict):
            data = [data]
        if not data:
            return Response(content="", media_type="text/csv")

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return Response(content=output.getvalue(), media_type="text/csv")

    else:
        return JSONResponse(content=data)
