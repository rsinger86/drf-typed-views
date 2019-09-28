## Django REST Framework - Typed Views

This project extends [Django Rest Framework](https://www.django-rest-framework.org/) to allow use of Python's type annotations for automatically validating and casting view parameters. This pattern makes for code that is easier to read and write: view inputs are individually declared, not buried inside all-encompassing `request` objects. You can also write less validation/sanitization code. 

More features:
- [Pydantic](https://pydantic-docs.helpmanual.io/) models and [TypeSystem](https://www.encode.io/typesystem/) schemas are compatible types for view parameters. Annotate your POST/PUT functions with them to automatically validate incoming request bodies and hydrate models.
- Advanced validators for more than just the type: `min_value`/`max_value` for numbers
- Validate string formats: `email`, `uuid` and `ipv4/6`; use Python's native `Enum` for `choices` validation

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
  * [Combining Different Parameter Types](##combining-different-parameter-types)
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

Unless a default value is given, the parameter is **required** and a `ValidationError` will be raised if not set.

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

### Combining Different Parameter Types

Todo...

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



### Accessing the Request Object


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

The core arguments to these classes are:
- `default` (the default value for the parameter, which is required unless set)
- `source` (if the view parameter has a different name than the value embedded in the request)

### Query
Use the `source` argument to alias the parameter value. For example, your query parameters can have dashes (`?starting-after=2019-09-09`) can be mapped to a parameter named `starting_after`. Also see this example for how to use `*` for `source` to map all the query parameters to a `dict` that populates a complex schema.

### Path
Use the `source` argument to alias a view parameter name.

### Body
By default, the entire request body is used to populate parameters marked with this class (`source="*"`). However, you can use specify nested fields in the request body, with support for dot notation.

```python
    def create_user(
        first_name: str = Body(source="first_name"),
        last_name: str = Body(source="last_name"),
        phone: str = Body(source="contact.phone_number")
    )
```

### CurrentUser
Todo...

## Supported Types and Validator Rules

The following native Python types are supported. Depending on the type, you can pass additional validation rules to the request element class (`Query`, `Path`, `Body`). You can think of the type combining with the validation rules to create a Django REST serializer field on the fly -- in fact, that's what happens behind the scenes.

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

### str

### bool

### datetime

### date

### time

### timedelta

### List

### Enum

### typesystem.Schema

### pydantic.BaseModel

### marshmallow.Schema

## Motivation

While REST Framework's ModelViewSets and ModelSerializers are very productive when building out CRUD resources, I've felt less productive in the framework when developing other types of operations. Serializers are a powerful and flexible way to validate incoming request data, but are not as self-documenting as type annotations. Furthermore, the Django ecosystem is hugely productive and I see no reason why REST Framework cannot take advantage of more Python 3 features.

## Inspiration

I first came across type annotations for validation in [API Star](https://github.com/encode/apistar), which has since evolved into an OpenAPI toolkit. This pattern was also offered by [Hug](https://hugapi.github.io/hug/) and [Molten](https://github.com/Bogdanp/molten) (I believe in that order). Furthermore, I've borrowed ideas from [FastAPI](https://github.com/tiangolo/fastapi), specifically its use of default values to declare additional validation rules. Finally, this [blog post](https://instagram-engineering.com/types-for-python-http-apis-an-instagram-story-d3c3a207fdb7) from Instagram's engineering team showed me how decorators can be used to implement these features on view functions.

