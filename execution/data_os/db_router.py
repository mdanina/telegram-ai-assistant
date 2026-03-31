#!/usr/bin/env python3
"""
Data OS: Domain Router

Routes data operations to the correct business domain
(product / secondary_product / personal) based on content analysis.
"""

DOMAINS = {"product", "secondary_product", "personal"}

# Maps metrics `source` column values to business domains
SOURCE_DOMAIN_MAP = {
    "Product": "product",
    "YandexMetrika": "product",
    "Yandex Metrika": "product",
    "YouTube": "personal",
    "GoogleAnalytics": "personal",
    "Google Analytics": "personal",
    "Sheets": "personal",
    "Google Sheets": "personal",
}

_PRODUCT_KEYWORDS = (
    "your_product", "product", "клиент", "специалист",
    "консультац", "маршрут", "sdq", "чекап",
    "координатор", "сессия", "нейропсихолог", "логопед",
    "терапи", "диагностик", "родител", "ребён", "ребенк",
)

_SECONDARY_KEYWORDS = (
    "secondary_product", "доп_продукт", "доппрод", "курс", "обучен",
)


def classify_domain(text: str) -> str:
    """Classifies text into a business domain.

    Returns 'product', 'secondary_product', or 'personal' (default).
    """
    if not text:
        return "personal"

    lower = text.lower()

    if any(kw in lower for kw in _PRODUCT_KEYWORDS):
        return "product"

    if any(kw in lower for kw in _SECONDARY_KEYWORDS):
        return "secondary_product"

    return "personal"


def get_domain_for_source(source: str) -> str:
    """Returns domain for a metrics source value."""
    return SOURCE_DOMAIN_MAP.get(source, "personal")
