from ninja import FilterSchema


class ExpenseSchemaFilter(FilterSchema):
    location: int | None = None
