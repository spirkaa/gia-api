from django import template

register = template.Library()


@register.filter
def rupluralize(value, arg):
    """
    Chooses the appropriate noun form depending on the number.

    :type value: int
    :param value: number
    :type arg: str
    :param arg: noun forms
    :return: noun
    :rtype: str

    {{ employees.count|rupluralize:"работник,работника,работников" }}
    """

    forms = arg.split(",")
    number = abs(int(value))
    a = number % 10
    b = number % 100

    if (a == 1) and (b != 11):
        return forms[0]
    elif (a >= 2) and (a <= 4) and ((b < 10) or (b >= 20)):  # noqa: RET505
        return forms[1]
    else:
        return forms[2]
