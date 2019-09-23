## Django REST Framework - Typed Views

This project extends [Django Rest Framework](https://www.django-rest-framework.org/) to allow use of Python's type annotations for automatically validating and casting view parameters. This pattern makes for readable, ergonomic code: views/controllers for web APIs read like functions with well-defined parameters, not buried inside  all-encompassing `request` objects. It also removes the need for repetitive validation logic.

[Pydantic](https://pydantic-docs.helpmanual.io/) models are compatible types for view parameters -- meaning you can use them to automatically validate POST data as an alternative to DRF's serializers.

```python
# urls.py
urlpatterns = [url(r"^movies/(?P<year>\d{4}-\d{2}-\d{2})/", search_movies_by_year)]

# ValidationError raised if request params do not match types
@typed_api_view(["GET"])
def search_movies_by_year(
    year: date, # from URL
    title: str, # from query params
    actors: List[str] = None, # from query params; has default, so optional
):
```

## Inspiration

I first came across type annotations for validation in APIStar, which has since evolved into an APItoolkit. This pattern was also introduced and used by [Hug](https://hugapi.github.io/hug/) and [Molten](https://github.com/Bogdanp/molten) (I believe in that order). Furthermore, I've borrowed ideas from FastAPI, specifically its use of default values to declare additional validation rules. Finally, this [blog post](https://instagram-engineering.com/types-for-python-http-apis-an-instagram-story-d3c3a207fdb7) from Instagram's engineering team showed me how decorators can be used to implement these features on view functions.

## Motivation

While REST Framework's ModelViewSets and ModelSerializers are very productive when building out CRUD resources, I've felt less productive in the framework when developing other types of operations. Serializers are a powerful and flexible way to validate incoming request data, but are not as self-documenting as the type annotation approach. Furthermore, the Django ecosystem is hugely productive and I see no reason why REST Framework cannot also take advantage of Python 3 features, just like the libraries and frameworks mentioned above.