## Django REST Framework - Typed Views

This project extends [Django Rest Framework](https://www.django-rest-framework.org/) to allow use of Python's type annotations for automatically validating and casting view parameters. This pattern makes for code that is easier to read and write: inputs for views are individually declared, not buried inside all-encompassing `request` objects, and require less repetitive validation/sanitization code.

More features:
- [Pydantic](https://pydantic-docs.helpmanual.io/) models and [TypeSystem](https://www.encode.io/typesystem/) schemas are compatible types for view parameters. Annotate your POST/PUT functions with them to automatically validate incoming request bodies and hydrate models.
- Advanced validators for more than just the type:
  - apply `min_value`/`max_value` rules to incoming numbers
  - validate string formats like `email`, `uuid` and `ipv4/6`
  - use Python's native `Enum` type for `choices` validation

Quick example:
```python
class UserType(Enum):
    trial = "trial"
    registered = "registered"

@typed_api_view(["GET"])
def get_users(
    type: UserType,
    registered_after: date = None, 
    login_count__gte: int = None,
    groups: List[str] = None,
    is_staff: bool = None
):
    print(type, registered_after, login_count__gte, groups, is_staff)
```

GET `/users/registered/?registered_after=2019-03-03&logins__gte=3&groups=admin,manager&is_staff=yes`<br>
:ok: Status Code: 200
```
    'registered'  date(2019, 3, 03)   3  ['admin', 'manager']  True
```

GET `/users/troll/?registered_after=9999&logins__gte=hugge&groups=1&is_staff=maybe`<br>
:no_entry_sign: Status Code: 400 *ValidationError raised* 
```json
    {
        "type": "`troll` is not a valid for UserType",
        "registered_after": "'9999' is not a valid date",
        "logins__gte": "'hugge' is not a valid integer",
        "groups": "1 is not a valid string",
        "is_staff": "'maybe' is not a valid boolean"
    }
```

## Inspiration

I first came across type annotations for validation in [API Star](https://github.com/encode/apistar), which has since evolved into an OpenAPI toolkit. This pattern was also offered by [Hug](https://hugapi.github.io/hug/) and [Molten](https://github.com/Bogdanp/molten) (I believe in that order). Furthermore, I've borrowed ideas from [FastAPI](https://github.com/tiangolo/fastapi), specifically its use of default values to declare additional validation rules. Finally, this [blog post](https://instagram-engineering.com/types-for-python-http-apis-an-instagram-story-d3c3a207fdb7) from Instagram's engineering team showed me how decorators can be used to implement these features on view functions.

## Motivation

While REST Framework's ModelViewSets and ModelSerializers are very productive when building out CRUD resources, I've felt less productive in the framework when developing other types of operations. Serializers are a powerful and flexible way to validate incoming request data, but are not as self-documenting as type annotations. Furthermore, the Django ecosystem is hugely productive and I see no reason why REST Framework cannot take advantage of more Python 3 features.

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

Todo...

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



## Supported Types and Validator Rules

The following native Python types are supported. Depending on the type, you can pass additional validation rules to the request element class (`Query`, `Path`, `Body`). You can think of the type combining with the validation rules to create a Django REST serializer field on the fly (in fact, that's what happens behind the scenes).

### int

### float

### Decimal

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
