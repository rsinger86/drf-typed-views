import functools
import inspect
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Mapping, Tuple

from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response

from typed_views import CurrentUser, Path, Query, Param, typed_api_view


"""

http://localhost:8000/logs/2/?title=1231234&price=33.43&latitude=3.333333333333333&is_pretty=no&email=robert@hotmail.com&upper_alpha_string=CAT&identifier=cat&website=https://www.nytimes.com/&identity=e028aa46-8411-4c83-b970-76be868c9413&file=/tmp/test.html&ip=162.254.168.185&timestamp=2019-04-03T10:10&start_date=1200-05-05&start_time=20:19&duration=3%205555:45&bag=paper&numbers=1,2,3

"""


class BagOptions(str, Enum):
    paper = "paper"
    plastic = "plastic"


@typed_api_view(["GET"])
def get_logs(
    id: int,
    latitude: Decimal = Query(decimal_places=20),
    title: str = Query(min_length=6),
    price: float = Query(min_value=6),
    # user: User = CurrentUser(),
    is_pretty: bool = Query(),
    email: str = Query(format="email"),
    upper_alpha_string: str = Query(regex=r"^[A-Z]+$"),
    identifier: str = Query(format="slug"),
    website: str = Query(format="url"),
    identity: str = Query(format="uuid"),
    file: str = Query(format="file_path", path="/tmp/"),
    ip: str = Query(format="ipv4"),
    timestamp: datetime = Query(),
    start_date: date = Query(),
    start_time: time = Query(),
    duration: timedelta = Query(),
    bag_type: BagOptions = Query(source="bag"),
    numbers: List[int] = Query(child=Param(min_value=0)),
):
    return Response(
        {
            "id": id,
            "title": title,
            "price": price,
            "latitude": latitude,
            "is_pretty": is_pretty,
            "email": email,
            "upper_alpha_string": upper_alpha_string,
            "identifier": identifier,
            "website": website,
            "identity": identity,
            "file": file,
            "ip": ip,
            "timestamp": timestamp,
            "start_date": start_date,
            "start_time": start_time,
            "duration": duration,
            "bag_type": bag_type,
            "numbers": numbers,
        }
    )
