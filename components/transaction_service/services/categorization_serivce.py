from loguru import logger

from components.transaction_service.config import Config


class CategorizationService:
    def __init__(self, cfg: Config):
        self.keywords = {
            key.lower(): value for key, value in cfg.categorization.category_keywords.items()
        }
        self.default_category = cfg.categorization.default_category
        self.defined_categories = set(cfg.categorization.categories)

        logger.info(
            f"Сервис категоризации инициализирован. "
            f"Ключевые слова: {len(self.keywords)}, Категории: {self.defined_categories}"
        )

    def categorize_transaction(self, description: str | None) -> str:
        if not description:
            logger.debug("Нет описания, присвоена категория по умолчанию.")
            return self.default_category

        desc_lower = description.lower()
        for keyword, category in self.keywords.items():
            if keyword in desc_lower:
                logger.debug(f"Найдено ключевое слово '{keyword}' в '{description}', категория: {category}")
                return category

        logger.debug(f"Ключевые слова не найдены в '{description}', присвоена категория по умолчанию.")
        return self.default_category
