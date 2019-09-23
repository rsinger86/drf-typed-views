## Django REST Framework - Typed Views

This project extends [Django Rest Framework](https://www.django-rest-framework.org/) to allow use of Python's type annotations for automatically validating and casting view parameters. This pattern makes for code that is easier to read and write: arguments for views are nicely detailed/enumerated, not buried inside all-encompassing `request` objects, and you can stop writing repetitive validation logic.

More features:
- [Pydantic](https://pydantic-docs.helpmanual.io/) models and [TypeSystem](https://www.encode.io/typesystem/) schemas are compatible types for view parameters. Annotate your POST/PUT functions with them to automatically validate incoming request bodies and hydrate models.
- Advanced validators for more than just the type:
  - apply `min_value`/`max_value` rules to incoming numbers
  - validate string formats like `email`, `uuid` and `ipv4/6`
  - validate lists, applying all the same rules to the items
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

**200** - GET `/users/registered/?registered_after=2019-03-03&login_count__gte=3&groups=admin,manager&is_staff=yes`
```
    'registered'  date(2019, 3, 03)   3  ['admin', 'manager']  True
```

**400** - GET `/users/banned/?registered_after=9999-99-99&login_count__gte=huge number&groups=1,4&is_staff=maybe`

```json
    {
        "type": "`troll` is not a valid for UserType",
        "registered_after": "'9999-99-99' is not a valid date",
        "login_count__gte": "'huge number' is not a valid integer",
        "groups": "1 is not a valid string",
        "is_staff": "'maybe' is not a valid boolean"

    }
```

## Inspiration

I first came across type annotations for validation in APIStar, which has since evolved into an APItoolkit. This pattern was also introduced and used by [Hug](https://hugapi.github.io/hug/) and [Molten](https://github.com/Bogdanp/molten) (I believe in that order). Furthermore, I've borrowed ideas from FastAPI, specifically its use of default values to declare additional validation rules. Finally, this [blog post](https://instagram-engineering.com/types-for-python-http-apis-an-instagram-story-d3c3a207fdb7) from Instagram's engineering team showed me how decorators can be used to implement these features on view functions.

## Motivation

While REST Framework's ModelViewSets and ModelSerializers are very productive when building out CRUD resources, I've felt less productive in the framework when developing other types of operations. Serializers are a powerful and flexible way to validate incoming request data, but are not as self-documenting as the type annotation approach. Furthermore, the Django ecosystem is hugely productive and I see no reason why REST Framework cannot also take advantage of Python 3 features, just like the libraries and frameworks mentioned above.

## How It Works: Simple Usage

For many cases, you can rely on some implicit behavior for how different parts of the request (URL path variables, query parameters, body) map to the parameters of a view function/method. 

*The value of a view parameter will come from...*
- a URL path variable if that path variable and the view argument have the same name, **or**:
- the request body if the view argument is annotated using a class from a supported library for complex object validation (Pydantic, TypeSystem), **or**
- a query parameter with the same name, if neither of the first rules apply

Furthermore, the parameter is required, unless a default value is given.

## How It Works: Advanced Usage