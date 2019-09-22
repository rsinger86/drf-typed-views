## Django REST Framework - Typed Views

This project extends Django Rest Framework to allow use of Python's type annotations for automatically validating and casting view parameters. This pattern makes for readable, ergonomic code: views/controllers for web APIs read like functions with well-defined parameters, not buried inside an all-encompassing `request` object. It also removes the need for repetitive validation logic. 

```python
# urls.py
urlpatterns = [url(r"^movies/(?P<year>\d{4}-\d{2}-\d{2})/", search_movies_by_year)]

# views.py
# ValidationError automatically raised if request params do not match types
@typed_api_view(["GET"])
def search_movies_by_year(
    year: date, # from URL
    title: str, # from query params
    actors: List[str] = None, # from query params; has default, so optional 
    duration: timedelta = None # from query params; has default, so optional 
):
```

## Inspiration

I first came across type annotations for validation in APIStar, which has since evolved into an APItoolkit. This pattern was also introduced by Hug and Molten (I believe in that order). Furthermore, I've borrowed ideas from FastAPI, specifically its use of default values to declare additional validation rules. Finally, this (blog post)[https://instagram-engineering.com/types-for-python-http-apis-an-instagram-story-d3c3a207fdb7] from Instagram's engineering team showed me how decorators can be used to implement these features on view functions.