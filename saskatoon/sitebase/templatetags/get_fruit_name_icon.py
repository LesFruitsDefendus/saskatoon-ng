from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

FRUIT_NAME_ICONS = {
    "Grapes": "🍇",
    "Melon": "🍈",
    "Watermelon": "🍉",
    "Tangerine": "🍊",
    "Lemon": "🍋",
    "Banana": "🍌",
    "Pineapple": "🍍",
    "Mango": "🥭",
    "Red Apple": "🍎",
    "Green Apple": "🍏",
    "Pear": "🍐",
    "Peach": "🍑",
    "Cherries": "🍒",
    "Strawberry": "🍓",
    "Kiwi": "🥝",
    "Tomato": "🍅",
    "Coconut": "🥥",
    # ? from fixtures
    "Cerise sucrée": "🍒",
    "Cerise griotte": "🍒",
    "Framboise": "🍒",
    "Fraise": "🍓",
    "Noix de Grenoble": "🥜",
    "Pêche": "🍑",
    "Poire rouge": "🍐",
    "Poire jaune": "🍐",
    "Poire vert": "🍐",
    "Asian pear": "🍐",
    "Pomme verte": "🍏",
    "Pommette": "🍎",
    "Pomme rouge": "🍎",
    "Pomme jaune": "🍎",
    "Rhubarbe": "🥕",
    "Figue": "🌰",
    "Raisin mauve (bleu)": "🍇",
    "Green grape": "🍇",
    "Red grapes": "🍇",
}


@register.filter
@stringfilter
def get_fruit_name_icon(fruit_name: str) -> str:
    """Returns the icon mapped to the tree's fruit name"""
    try:
        icon: str = FRUIT_NAME_ICONS[fruit_name]
    except KeyError:
        return "⬛"
    return icon
