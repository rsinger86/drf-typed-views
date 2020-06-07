## Django REST Framework - Typed Views

[![Package version](https://badge.fury.io/py/drf-typed-views.svg)](https://pypi.python.org/pypi/drf-typed-views)
[![Python versions](https://img.shields.io/pypi/status/drf-typed-views.svg)](https://img.shields.io/pypi/status/drf-typed-views.svg/)

This project extends [Django Rest Framework](https://www.django-rest-framework.org/) to allow use of Python's type annotations for automatically validating and casting view parameters. This pattern makes for code that is easier to read and write. View inputs are individually declared, not buried inside all-encompassing `request` objects. Meanwhile, you get even more out of type annotations: they can replace repetitive validation/sanitization code. 

More features:
- [Pydantic](https://pydantic-docs.helpmanual.io/) models and [Marshmallow](https://marshmallow.readthedocs.io) schemas are compatible types for view parameters. Annotate your POST/PUT functions with them to automatically validate incoming request bodies.
- Advanced validators for more than just the type: `min_value`/`max_value` for numbers
- Validate string formats: `email`, `uuid` and `ipv4/6`; use Python's native `Enum` for "choices" validation

Quick example:
```python
from rest_typed_views import typed_api_view

@typed_api_view(["GET"])
def get_users(registered_on: date = None, groups: List[int] = None, is_staff: bool = None):
    print(registered_on, groups, is_staff)
```

GET `/users/registered/?registered_on=2019-03-03&groups=4,5&is_staff=yes`<br>
Status Code: 200
```
    date(2019, 3, 3)   [4, 5]  True
```

GET `/users/?registered_on=9999&groups=admin&is_staff=maybe`<br>
:no_entry_sign: Status Code: 400 *ValidationError raised* 
```json
    {
        "registered_on": "'9999' is not a valid date",
        "groups": "'admin' is not a valid integer",
        "is_staff": "'maybe' is not a valid boolean"
    }
```
## Table of Contents
* [Install & Decorators](#install--decorators)
* [How It Works: Simple Usage](#how-it-works-simple-usage)
  * [Basic GET Request](#basic-get-request)
  * [Basic POST Request](#basic-post-request)
* [How It Works: Advanced Usage](#how-it-works-advanced-usage)
  * [Additional Validation Rules](#additional-validation-rules)
  * [Nested Body Fields](#nested-body-fields)
  * [List Validation](#list-validation)
  * [Accessing the Request Object](#accessing-the-request-object)
  * [Interdependent Query Parameter Validation](#interdependent-query-parameter-validation)
  * [(Simple) Access Control](#simple-access-control)
* [Enabling Marshmallow, Pydantic Schemas](#enabling-3rd-party-validators)
* [Request Element Classes](#request-element-classes)
  * [Query](#query)
  * [Body](#body)
  * [Path](#path)
  * [Header](#header)
  * [CurrentUser](#currentuser)
* [Supported Types/Validator Rules](#supported-types-and-validator-rules)
  * [int](#int)
  * [float](#float)
  * [Decimal](#decimal)
  * [str](#str)
  * [bool](#bool)
  * [datetime](#datetime)
  * [date](#date)
  * [time](#time)
  * [timedelta](#timedelta)
  * [List](#list)
  * [Enum](#enum)
  * [marshmallow.Schema](#marshmallowschema)
  * [pydantic.BaseModel](#pydanticbasemodel)
* [Change Log](#changes)
* [Motivation & Inspiration](#motivation)

## Install & Decorators

```
pip install drf-typed-views
```

You can add type annotation-enabled features to either `ViewSet` methods or function-based views using the `typed_action` and `typed_api_view` decorators. They take the exact same arguments as Django REST's [`api_view`](https://www.django-rest-framework.org/api-guide/views/#api_view) and [`action`](https://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing) decorators.

## How It Works: Simple Usage

For many cases, you can rely on implicit behavior for how different parts of the request (URL path variables, query parameters, body) map to the parameters of a view function/method. 

The value of a view parameter will come from...
- the URL path if the path variable and the view argument have the same name, *or*:
- the request body if the view argument is annotated using a class from a supported library for complex object validation (Pydantic, MarshMallow), *or*:
- a query parameter with the same name

Unless a default value is given, the parameter is **required** and a [`ValidationError`](https://www.django-rest-framework.org/api-guide/exceptions/#validationerror) will be raised if not set.

### Basic GET Request
```python
urlpatterns = [
    url(r"^(?P<city>[\w+])/restaurants/", search_restaurants)
]

from rest_typed_views import typed_api_view

# Example request: /chicago/restaurants?delivery=yes
@typed_api_view(["GET"])
def search_restaurants(city: str, rating: float = None, offers_delivery: bool = None):
    restaurants = Restaurant.objects.filter(city=city)

    if rating is not None:
        restaurants = restaurants.filter(rating__gte=rating)

    if offers_delivery is not None:
        restaurants = restaurants.filter(delivery=offers_delivery)
```

In this example, `city` is required and must be its string. Its value comes from the URL path variable with the same name. The other parameters, `rating` and `offers_delivery`, are not part of the path parameters and are assumed to be query parameters. They both have a default value, so they are optional.

### Basic POST Request 
```python
# urls.py
urlpatterns = [url(r"^(?P<city>[\w+])/bookings/", create_booking)]

# settings.py
DRF_TYPED_VIEWS = {"schema_packages": ["pydantic"]}

# views.py
from pydantic import BaseModel
from rest_typed_views import typed_api_view


class RoomEnum(str, Enum):
    double = 'double'
    twin = 'twin'
    single = 'single'


class BookingSchema(BaseModel):
    start_date: date
    end_date: date
    room: RoomEnum = RoomEnum.double
    include_breakfast: bool = False

# Example request: /chicago/bookings/
@typed_api_view(["POST"])
def create_booking(city: str, booking: BookingSchema):
    # do something with the validated booking...
```

In this example, `city` will again be populated using the URL path variable. The `booking` parameter is annotated using a supported complex schema class (Pydantic), so it's assumed to come from the request body, which will be read in as JSON, used to hydrate the Pydantic `BookingSchema` and then validated. If validation fails a `ValidationError` will be raised.

## How It Works: Advanced Usage

For more advanced use cases, you can explicitly declare how each parameter's value is sourced from the request -- from the query parameters, path, body or headers -- as well as define additional validation rules. You import a class named after the request element that is expected to hold the value and assign it to the parameter's default.

```python
from rest_typed_views import typed_api_view, Query, Path

@typed_api_view(["GET"])
def list_documents(year: date = Path(), title: str = Query(default=None)):
    # ORM logic here...
```

In this example, `year` is required and must come from the URL path and `title` is an optional query parameter because the `default` is set. This is similar to Django REST's [serializer fields](https://www.django-rest-framework.org/api-guide/fields/#core-arguments):  passing a default implies that the filed is not required. 

```python
from rest_typed_views import typed_api_view, Header

@typed_api_view(["GET"])
def get_cache_header(cache: str = Header()):
    # ORM logic here...
```

In this example, `cache` is required and must come from the headers. 

### Additional Validation Rules

You can use the request element class (`Query`, `Path`, `Body`, `Header`) to set additional validation constraints. You'll find that these keywords are consistent with Django REST's serializer fields.

```python
from rest_typed_views import typed_api_view, Query, Path

@typed_api_view(["GET"])
def search_restaurants(
    year: date = Path(), 
    rating: int = Query(default=None, min_value=1, max_value=5)
):
    # ORM logic here...


@typed_api_view(["GET"])
def get_document(id: str = Path(format="uuid")):
    # ORM logic here...


@typed_api_view(["GET"])
def search_users(
    email: str = Query(default=None, format="email"), 
    ip_address: str = Query(default=None, format="ip"), 
):
    # ORM logic here...
```

View a [full list](#supported-types-and-validator-rules) of supported types and additional validation rules.

### Nested Body Fields

Similar to how `source` is used in Django REST to control field mappings during serialization, you can use it to specify the exact path to the request data.

```python
from pydantic import BaseModel
from rest_typed_views import typed_api_view, Query, Path

class Document(BaseModel):
    title: str
    body: str

"""
    POST
    {
        "strict": false,
        "data": {
            "title": "A Dark and Stormy Night",
            "body": "Once upon a time"
        }
    }
"""
@typed_api_view(["POST"])
def create_document(
    strict_mode: bool = Body(source="strict"), 
    item: Document = Body(source="data")
):
    # ORM logic here...
```
You can also use dot-notation to source data multiple levels deep in the JSON payload.

### List Validation

For the basic case of list validation - validating types within a comma-delimited string - declare the type to get automatic validation/coercion:

```python
from rest_typed_views import typed_api_view, Query

@typed_api_view(["GET"])
def search_movies(item_ids: List[int] = [])):
    print(item_ids)

# GET /movies?items_ids=41,64,3
# [41, 64, 3]
```

But you can also specify `min_length` and `max_length`, as well as the `delimiter` and specify additional rules for the child items -- think Django REST's [ListField](https://www.django-rest-framework.org/api-guide/fields/#listfield).

Import the generic `Param` class and use it to set the rules for the `child` elements:

```python
from rest_typed_views import typed_api_view, Query, Param

@typed_api_view(["GET"])
def search_outcomes(
    scores: List[int] = Query(delimiter="|", child=Param(min_value=0, max_value=100))
):
    # ORM logic ...

@typed_api_view(["GET"])
def search_message(
    recipients: List[str] = Query(min_length=1, max_length=10, child=Param(format="email"))
):
    # ORM logic ...
```

### Accessing the Request Object

You probably won't need to access the `request` object directly, as this package will provide its relevant properties as view arguments. However, you can include it as a parameter annotated with its type and it will be injected:

```python
from rest_framework.request import Request
from rest_typed_views import typed_api_view

@typed_api_view(["GET"])
def search_documens(request: Request, q: str = None):
    # ORM logic ...
```

### Interdependent Query Parameter Validation
Often, it's useful to validate a combination of query parameters - for instance, a `start_date` shouldn't come after an `end_date`. You can use complex schema object (Pydantic or Marshmallow) for this scenario. In the example below, `Query(source="*")` is instructing an instance of `SearchParamsSchema` to be populated/validated using all of the query parameters together: `request.query_params.dict()`.  

```python
from marshmallow import Schema, fields, validates_schema, ValidationError
from rest_typed_views import typed_api_view

class SearchParamsSchema(Schema):
    start_date = fields.Date()
    end_date = fields.Date()

    @validates_schema
    def validate_numbers(self, data, **kwargs):
        if data["start_date"] >= data["end_date"]:
            raise ValidationError("end_date must come after start_date")

@typed_api_view(["GET"])
def search_documens(search_params: SearchParamsSchema = Query(source="*")):
    # ORM logic ...
```

### (Simple) Access Control

You can apply some very basic access control by applying some validation rules to a view parameter sourced from the `CurrentUser` request element class. In the example below, a `ValidationError` will be raised if the `request.user` is not a member of either `super_users` or `admins`.

```python
    from my_pydantic_schemas import BookingSchema
    from rest_typed_views import typed_api_view, CurrentUser

    @typed_api_view(["POST"])
    def create_booking(
        booking: BookingSchema, 
        user: User = CurrentUser(member_of_any=["super_users", "admins"])
    ):
        # Do something with the request.user
```

Read more about the [`Current User` request element class](#current-user-keywords).

## Enabling Marshmallow, Pydantic Schemas <a id="enabling-3rd-party-validators"></a>

As an alternative to Django REST's serializers, you can annotate views with [Pydantic](https://pydantic-docs.helpmanual.io/) models or [Marshmallow](https://marshmallow.readthedocs.io/en/stable/) schemas to have their parameters automatically validated and pass an instance of the Pydantic/Marshmallow class to your method/function.

To enable support for third-party libraries for complex object validation, modify your settings:

```python
DRF_TYPED_VIEWS = {
    "schema_packages": ["pydantic", "marshmallow"]
}
```

These third-party packages must be installed in your virtual environment/runtime.

## Request Element Classes

You can specify the part of the request that holds each view parameter by using default function arguments, for example:
```python
    from rest_typed_views import Body, Query

    @typed_api_view(["PUT"])
    def update_user(
        user: UserSchema = Body(), 
        optimistic_update: bool = Query(default=False)
    ):
```

The `user` parameter will come from the request body and is required because no default is provided. Meanwhile, `optimistic_update` is not required and will be populated from a query parameter with the same name. 

The core keyword arguments to these classes are:
- `default` the default value for the parameter, which is required unless set
- `source` if the view parameter has a different name than its key embedded in the request

Passing keywords for additional validation constraints is a *powerful capability* that gets you *almost the same feature set* as Django REST's flexible [serializer fields](https://www.django-rest-framework.org/api-guide/fields/). See a [complete list](#supported-types-and-validator-rule) of validation keywords.


### Query
Use the `source` argument to alias the parameter value and pass keywords to set additional constraints. For example, your query parameters can have dashes, but be mapped to a parameter that have underscores:

```python
    from rest_typed_views import typed_api_view, Query

    @typed_api_view(["GET"])
    def search_events(
        starting_after: date = Query(source="starting-after"),
        available_tickets: int = Query(default=0, min_value=0)
    ):
        # ORM logic here...
```

### Body
By default, the entire request body is used to populate parameters marked with this class (`source="*"`):

```python
    from rest_typed_views import typed_api_view, Body
    from my_pydantic_schemas import ResidenceListing

    @typed_api_view(["POST"])
    def create_listing(residence: ResidenceListing = Body()):
        # ORM logic ...
```

However, you can also specify nested fields in the request body, with support for dot notation.

```python
    """
        POST  /users/
        {
            "first_name": "Homer",
            "last_name": "Simpson",
            "contact": {
                "phone" : "800-123-456",
                "fax": "13235551234"
            }
        }
    """
    from rest_typed_views import typed_api_view, Body

    @typed_api_view(["POST"])
    def create_user(
        first_name: str = Body(source="first_name"),
        last_name: str = Body(source="last_name"),
        phone: str = Body(source="contact.phone", min_length=10, max_length=20)
    ):
        # ORM logic ...
```

### Path
Use the `source` argument to alias a view parameter name. More commonly, though, you can set additional validation rules for parameters coming from the URL path. 

```python
    from rest_typed_views import typed_api_view, Query

    @typed_api_view(["GET"])
    def retrieve_event(id: int = Path(min_value=0, max_value=1000)):
        # ORM logic here...
```

### Header
Use the `Header` request element class to automatically retrieve a value from a header. Underscores in variable names are automatically converted to dashes. 

```python
    from rest_typed_views import typed_api_view, Header

    @typed_api_view(["GET"])
    def retrieve_event(id: int, cache_control: str = Header(default="no-cache")):
        # ORM logic here...
```

If you prefer, you can explicitly specify the exact header key:
```python
    from rest_typed_views import typed_api_view, Header

    @typed_api_view(["GET"])
    def retrieve_event(id: int, cache_control: str = Header(source="cache-control", default="no-cache")):
        # ORM logic here...
```

### CurrentUser <a id="current-user-keywords"></a>

Use this class to have a view parameter populated with the current user of the request. You can even extract fields from the current user using the `source` option.

```python
    from my_pydantic_schemas import BookingSchema
    from rest_typed_views import typed_api_view, CurrentUser

    @typed_api_view(["POST"])
    def create_booking(booking: BookingSchema, user: User = CurrentUser()):
        # Do something with the request.user

    @typed_api_view(["GET"])
    def retrieve_something(first_name: str = CurrentUser(source="first_name")):
        # Do something with the request.user's first name
```
You can also pass some additional parameters to the `CurrentUser` request element class to implement simple access control:
- `member_of` (str) Validates that the current `request.user` is a member of a group with this name
- `member_of_any` (List[str]) Validates that the current `request.user` is a member of one of these groups

*Using these keyword validators assumes that your `User` model has a many-to-many relationship with `django.contrib.auth.models.Group` via `user.groups`.*

An example:

```python
from django.contrib.auth.models import User
from rest_typed_views import typed_api_view, CurrentUser

@typed_api_view(["GET"])
def do_something(user: User = CurrentUser(member_of="admin")):
    # now have a user instance (assuming ValidationError wasn't raised)
```
## Supported Types and Validator Rules

The following native Python types are supported. Depending on the type, you can pass additional validation rules to the request element class (`Query`, `Path`, `Body`). You can think of the type combining with the validation rules to create a Django REST serializer field on the fly -- in fact, that's what happens behind the scenes.

### str
Additional arguments:
- `max_length` Validates that the input contains no more than this number of characters.
- `min_length` Validates that the input contains no fewer than this number of characters.
- `trim_whitespace` (bool; default `True`) Whether to trim leading and trailing white space.
- `format` Validates that the string matches a common format; supported values:
    - `email` validates the text to be a valid e-mail address.
    - `slug` validates the input against the pattern `[a-zA-Z0-9_-]+`.
    - `uuid` validates the input is a valid UUID string
    - `url` validates fully qualified URLs of the form `http://<host>/<path>`
    - `ip` validates input is a valid IPv4 or IPv6 string
    - `ipv4` validates input is a valid IPv4 string
    - `ipv6` validates input is a valid IPv6 string
    - `file_path` validates that the input corresponds to filenames in a certain directory on the filesystem; allows all the same keyword arguments as Django REST's [`FilePathField`](https://www.django-rest-framework.org/api-guide/fields/#filepathfield)

Some examples:

```python
from rest_typed_views import typed_api_view, Query

@typed_api_view(["GET"])
def search_users(email: str = Query(format='email')):
    # ORM logic here...
    return Response(data)

@typed_api_view(["GET"])
def search_shared_links(url: str = Query(default=None, format='url')):
    # ORM logic here...
    return Response(data)

@typed_api_view(["GET"])
def search_request_logs(ip_address: str = Query(default=None, format='ip')):
    # ORM logic here...
    return Response(data)
```

### int
Additional arguments:
- `max_value` Validate that the number provided is no greater than this value.
- `min_value` Validate that the number provided is no less than this value.

An example:
```python
from rest_typed_views import typed_api_view, Query

@typed_api_view(["GET"])
def search_products(inventory: int = Query(min_value=0)):
    # ORM logic here...
```

### float
Additional arguments:
- `max_value` Validate that the number provided is no greater than this value.
- `min_value` Validate that the number provided is no less than this value.

An example:
```python
from rest_typed_views import typed_api_view, Query

@typed_api_view(["GET"])
def search_products(price: float = Query(min_value=0)):
    # ORM logic here...
```

### Decimal
Additional arguments:
- `max_value` Validate that the number provided is no greater than this value.
- `min_value` Validate that the number provided is no less than this value.
- .. even more ... accepts the same arguments as [Django REST's `DecimalField`](https://www.django-rest-framework.org/api-guide/fields/#decimalfield)

### bool
View parameters annotated with this type will validate and coerce the same values as Django REST's `BooleanField`, including but not limited to the following:
```python
    true_values = ["yes", 1, "on", "y", "true"]
    false_values = ["no", 0, "off", "n", "false"]
```

### datetime
Additional arguments:
- `input_formats` A list of input formats which may be used to parse the date-time, defaults to Django's `DATETIME_INPUT_FORMATS` settings, which defaults to `['iso-8601']`
- `default_timezone`  A `pytz.timezone` of the timezone. If not specified, falls back to Django's `USE_TZ` setting.

### date
Additional arguments:
- `input_formats` A list of input formats which may be used to parse the date, defaults to Django's `DATETIME_INPUT_FORMATS` settings, which defaults to `['iso-8601']`

### time
Additional arguments:
- `input_formats` A list of input formats which may be used to parse the time, defaults to Django's `TIME_INPUT_FORMATS` settings, which defaults to `['iso-8601']`

### timedelta
Validates strings of the format `'[DD] [HH:[MM:]]ss[.uuuuuu]'` and converts them to a `datetime.timedelta` instance.

Additional arguments:
- `max_value` Validate that the input duration is no greater than this value.
- `min_value` Validate that the input duration is no less than this value.

### List
Validates strings of the format `'[DD] [HH:[MM:]]ss[.uuuuuu]'` and converts them to a `datetime.timedelta` instance.

Additional arguments:
- `min_length` Validates that the list contains no fewer than this number of elements.
- `max_length` Validates that the list contains no more than this number of elements.
- `child` Pass keyword constraints via a `Param` instance to to validate the members of the list.

An example:
```python
from rest_typed_views import typed_api_view, Param, Query

@typed_api_view(["GET"])
def search_contacts(emails: List[str] = Query(max_length=10, child=Param(format="email"))):
    # ORM logic here...
```

### Enum
Validates that the value of the input is one of a limited set of choices. Think of this as mapping to a Django REST [`ChoiceField`](https://www.django-rest-framework.org/api-guide/fields/#choicefield).

An example:
```python
from rest_typed_views import typed_api_view, Query

class Straws(str, Enum):
    paper = "paper"
    plastic = "plastic"

@typed_api_view(["GET"])
def search_straws(type: Straws = None):
    # ORM logic here...
```

### marshmallow.Schema
You can annotate view parameters with [Marshmallow schemas](https://marshmallow.readthedocs.io/en/stable/) to validate request data and pass an instance of the schema to the view.

```python
from marshmallow import Schema, fields
from rest_typed_views import typed_api_view, Query

class ArtistSchema(Schema):
    name = fields.Str()

class AlbumSchema(Schema):
    title = fields.Str()
    release_date = fields.Date()
    artist = fields.Nested(ArtistSchema())

"""
    POST 
    {
        "title": "Michael Scott's Greatest Hits",
        "release_date": "2019-03-03",
        "artist": {
            "name": "Michael Scott"
        }
    }
"""
@typed_api_view(["POST"])
def create_album(album: AlbumSchema):
    # now have an album instance (assuming ValidationError wasn't raised)
```

### pydantic.BaseModel
You can annotate view parameters with [Pydantic models](https://pydantic-docs.helpmanual.io/) to validate request data and pass an instance of the model to the view.

```python
from pydantic import BaseModel
from rest_typed_views import typed_api_view, Query

class User(BaseModel):
    id: int
    name: str
    signup_ts: datetime = None
    friends: List[int] = []

"""
    POST 
    {
        "id": 24529782,
        "name": "Michael Scott",
        "friends": [24529782]
    }
"""
@typed_api_view(["POST"])
def create_user(user: User):
    # now have a user instance (assuming ValidationError wasn't raised)
```

## Change Log

* June 7, 2020
  * Fixes compatability with DRF decorator. Thanks @sjquant!
  * Makes Django's QueryDict work with Marshmallow and Pydantic validators. Thanks @filwaline!
* February 2, 2020: Adds support for `Header` request parameter. Thanks @bbkgh!

## Motivation

While REST Framework's ModelViewSets and ModelSerializers are very productive when building out CRUD resources, I've felt less productive in the framework when developing other types of operations. Serializers are a powerful and flexible way to validate incoming request data, but are not as self-documenting as type annotations. Furthermore, the Django ecosystem is hugely productive and I see no reason why REST Framework cannot take advantage of more Python 3 features.

## Inspiration

I first came across type annotations for validation in [API Star](https://github.com/encode/apistar), which has since evolved into an OpenAPI toolkit. This pattern has also been offered by [Hug](https://hugapi.github.io/hug/) and [Molten](https://github.com/Bogdanp/molten) (I believe in that order). Furthermore, I've borrowed ideas from [FastAPI](https://github.com/tiangolo/fastapi), specifically its use of default values to declare additional validation rules. Finally, this [blog post](https://instagram-engineering.com/types-for-python-http-apis-an-instagram-story-d3c3a207fdb7) from Instagram's engineering team showed me how decorators can be used to implement these features on view functions.

