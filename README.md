## Django REST Framework - Typed Views

This project extends [Django Rest Framework](https://www.django-rest-framework.org/) to allow use of Python's type annotations for automatically validating and casting view parameters. This pattern makes for code that is easier to read and write. Wiew inputs are individually declared, not buried inside all-encompassing `request` objects. Meanwhile, you get even more out of type annotations as they can replace repetitive validation/sanitization code. 

More features:
- [Pydantic](https://pydantic-docs.helpmanual.io/) models and [TypeSystem](https://www.encode.io/typesystem/) schemas are compatible types for view parameters. Annotate your POST/PUT functions with them to automatically validate incoming request bodies.
- Advanced validators for more than just the type: `min_value`/`max_value` for numbers
- Validate string formats: `email`, `uuid` and `ipv4/6`; use Python's native `Enum` for "choices" validation

Quick example:
```python
from typed_views import typed_api_view

class UserType(Enum):
    trial = "trial"
    registered = "registered"

@typed_api_view(["GET"])
def get_users(
    type: UserType, registered_after: date = None, groups: List[str] = None, is_staff: bool = None
):
    print(type, registered_after, login_count__gte, groups, is_staff)
```

GET `/users/registered/?registered_after=2019-03-03&groups=admin,manager&is_staff=yes`<br>
Status Code: 200
```
    'registered'  date(2019, 3, 03)   ['admin', 'manager']  True
```

GET `/users/troll/?registered_after=9999&groups=1&is_staff=maybe`<br>
:no_entry_sign: Status Code: 400 *ValidationError raised* 
```json
    {
        "type": "`troll` is not a valid for UserType",
        "registered_after": "'9999' is not a valid date",
        "groups": "1 is not a valid string",
        "is_staff": "'maybe' is not a valid boolean"
    }
```
## Table of Contents
* [How It Works: Simple Usage](#how-it-works-simple-usage)
  * [Basic GET Request](#basic-get-request)
  * [Basic POST Request](#basic-post-request)
* [How It Works: Advanced Usage](#how-it-works-advanced-usage)
  * [Additional Validation Rules](#additional-validation-rules)
  * [Nested Body Fields](#nested-body-fields)
  * [List Validation](#list-validation)
  * [Accessing the Request Object](#accessing-the-request-object)
* [Request Element Classes](#request-element-classes)
  * [Query](#query)
  * [Body](#body)
  * [Path](#path)
* [Supported Types and Validator Rules](#supported-types-and-validator-rules)
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
  * [typesystem.Schema](#typesystemschema)
  * [pydantic.BaseModel](#pydanticbasemodel)
  * [marshmallow.Schema](#marshmallowschema)
* [Motivation & Inspiration](#motivation)

## How It Works: Simple Usage

For many cases, you can rely on some implicit behavior for how different parts of the request (URL path variables, query parameters, body) map to the parameters of a view function/method. 

The value of a view parameter will come from...
- the URL path if the path variable and the view argument have the same name, *or*:
- the request body if the view argument is annotated using a class from a supported library for complex object validation (Pydantic, TypeSystem), *or*
- a query parameter with the same name

Unless a default value is given, the parameter is **required** and a [`ValidationError`](https://www.django-rest-framework.org/api-guide/exceptions/#validationerror) will be raised if not set.

### Basic GET Request
```python
urlpatterns = [
    url(r"^(?P<city>[\w+])/restaurants/", search_restaurants)
]

from typed_views import typed_api_view


# Example request: /chicago/restaurnts?delivery=yes
@typed_api_view(["GET"])
def search_restaurants(
    city: str,
    rating: float = None,
    offers_delivery: bool = None,
):
    restaurants = Restaurant.objects.filter(city=city)

    if rating not None:
        restaurants = restaurants.filter(rating__gte=rating)

    if offers_delivery not None:
        restaurants = restaurants.filter(delivery=offers_delivery)
```

In this example, `city` is required and must be its string. Its value comes from the URL path variable with the same name. The other parameters, `rating` and `offers_delivery`, are not part of the path parameters and are assumed to be query parameters. They both have a default value, so they are optional.

### Basic POST Request 
```python
urlpatterns = [
    url(r"^(?P<city>[\w+])/bookings/", create_booking)
]

from pydantic import BaseModel
from typed_views import typed_api_view


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

For more advanced use cases, you can explicitly declare how each parameter's value is sourced from the request -- from the query parameters, path, body or headers -- as well as define additional validation rules.

You import a class named after the request element that is expected to hold the value and assign it to the parameter's default.

```python
from typed_views import typed_api_view, Query, Path

@typed_api_view(["GET"])
def list_documents(year: date = Path(), title: str = Query(default=None)):
    # ORM logic here...
```

In this example, `year` is required and must come from the URL path and `title` is an optional query parameter because the `default` is set. This is similar to Django REST's [serializer fields](https://www.django-rest-framework.org/api-guide/fields/#core-arguments):  passing a default implies that the filed is not required. 

### Additional Validation Rules

Using the request element class (Query, Path, Body) to set additional validation constraints. You'll find that these keywords are consistent with Django REST's serializer fields.

```python
from typed_views import typed_api_view, Query, Path

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

See a [full inventory](#supported-types-and-validator-rules) of supported types and additional validation rules.

### Nested Body Fields

Similar to how `source` is used in Django REST to control field mappings during serialization, you can use it to specify the exact path to the request data.

```python
from pydantic import BaseModel
from typed_views import typed_api_view, Query, Path

class Document(BaseModel):
    title: str
    body: str


@typed_api_view(["POST"])
def create_document(
    strict_mode: bool = Body(source="strict"), 
    item: Document = Body(source="data")
):
    # ORM logic here...
```
This function will expect a body like:
```json
{
    "strict": false,
    "data": {
        "title": "A Dark and Stormy Night",
        "body": "Once upon a time"
    }
}
```
You can also use dot-notation to source data multiple levels deep in the JSON payload.

### List Validation

For the basic case of list validation - validating the item type of comma-delimited string - declare the type to get automatic validation/coercion:

```python
from typed_views import typed_api_view, Query

@typed_api_view(["GET"])
def search_movies(item_ids: List[int] = [])):
    print(item_ids)

# GET /movies?items_ids=41,64,3
# [41, 64, 3]
```

But you can also specify `min_length` and `max_length`, as well as specify additional rules for the child items -- think Django REST's [ListField](https://www.django-rest-framework.org/api-guide/fields/#listfield).

Import the generic `Param` class and use it to set the rules for the `child` elements:

```python
from typed_views import typed_api_view, Query, Param

@typed_api_view(["GET"])
def search_outcomes(
    scores: List[int] = Query(default=[], child=Param(min_value=0, max_value=100))
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
from typed_views import typed_api_view

@typed_api_view(["GET"])
def search_documens(request: Request, q: str = None):
    # ORM logic ...
```

## Request Element Classes

You can specify the part of the request that holds each view parameter by using default function arguments, for example:
```python
    from typed_views import Body, Query

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

Passing keywords for additional validation constraints is a *powerful capability* that gets you *almost the same feature set* as Django REST's powerful [serializer fields](https://www.django-rest-framework.org/api-guide/fields/). See a [complete list](#supported-types-and-validator-rule) of validation keywords.


### Query
Use the `source` argument to alias the parameter value and pass keywords to set additional constraints. For example, your query parameters can have dashes, but be mapped to a parameter that have underscores:

```python
    from typed_views import typed_api_view, Query

    @typed_api_view(["GET"])
    def search_events(
        starting_after: date = Query(source="starting-after"),
        available_tickets: int = Query(default=0, min_value=0)
    ):
        # ORM logic here...
```

### Body
By default, the entire request body is used to populate parameters marked with this class(`source="*"`):

```python
    from typed_views import typed_api_view, Body
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
    from typed_views import typed_api_view, Body

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
    from typed_views import typed_api_view, Query

    @typed_api_view(["GET"])
    def retrieve_event(id: int = Path(min_value=0, max_value=1000)):
        # ORM logic here...
```

### CurrentUser

Todo...

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

### int
Additional arguments:
- `max_value` Validate that the number provided is no greater than this value.
- `min_value` Validate that the number provided is no less than this value.

### float
Additional arguments:
- `max_value` Validate that the number provided is no greater than this value.
- `min_value` Validate that the number provided is no less than this value.

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

### Enum

### typesystem.Schema

### pydantic.BaseModel

### marshmallow.Schema

## Motivation

While REST Framework's ModelViewSets and ModelSerializers are very productive when building out CRUD resources, I've felt less productive in the framework when developing other types of operations. Serializers are a powerful and flexible way to validate incoming request data, but are not as self-documenting as type annotations. Furthermore, the Django ecosystem is hugely productive and I see no reason why REST Framework cannot take advantage of more Python 3 features.

## Inspiration

I first came across type annotations for validation in [API Star](https://github.com/encode/apistar), which has since evolved into an OpenAPI toolkit. This pattern was also offered by [Hug](https://hugapi.github.io/hug/) and [Molten](https://github.com/Bogdanp/molten) (I believe in that order). Furthermore, I've borrowed ideas from [FastAPI](https://github.com/tiangolo/fastapi), specifically its use of default values to declare additional validation rules. Finally, this [blog post](https://instagram-engineering.com/types-for-python-http-apis-an-instagram-story-d3c3a207fdb7) from Instagram's engineering team showed me how decorators can be used to implement these features on view functions.

