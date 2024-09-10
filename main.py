import asyncio
from playwright.async_api import Playwright, async_playwright, Page
import csv
import logging
from typing import Dict, List, Tuple
import random

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Константы
CSV_FILENAME = "accounts_data.csv"
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
]


class AccountManager:
    def __init__(self, page: Page):
        self.page = page

    async def navigate(self, url: str) -> None:
        """Асинхронный переход по URL."""
        logger.info(f"Переход по URL: {url}")
        await self.page.goto(url)
        await self.page.wait_for_load_state('networkidle')

    async def fill_and_submit(self, selectors: Dict[str, str]) -> None:
        """Асинхронное заполнение полей формы и отправка."""
        for field, value in selectors.items():
            logger.info(f"Заполнение поля {field}")
            await self.page.fill(field, value)
        await self.page.press('input[type="submit"]', 'Enter')


class GoogleAccountManager(AccountManager):
    async def login(self, email: str, password: str) -> None:
        """Асинхронный вход в Google аккаунт."""
        logger.info(f"Вход в аккаунт Google: {email}")
        await self.navigate('https://accounts.google.com')
        await self.page.fill('input[type="email"]', email)
        await self.page.click('#identifierNext')
        await self.page.fill('input[type="password"]', password)
        await self.page.click('#passwordNext')

    async def change_details(self, current_password: str, new_password: str, first_name: str, last_name: str) -> None:
        """Асинхронное изменение данных Google аккаунта."""
        logger.info(f"Изменение данных аккаунта Google для пользователя: {first_name} {last_name}")
        await self.navigate('https://myaccount.google.com/personal-info')

        # Здесь должна быть реализация изменения имени и пароля
        # Примечание: эту часть нужно адаптировать под текущую структуру страницы аккаунта Google


class TwitterAccountManager(AccountManager):
    async def login(self, email: str, password: str) -> None:
        """Асинхронный вход в Twitter аккаунт."""
        logger.info(f"Вход в аккаунт Twitter: {email}")
        await self.navigate('https://twitter.com/login')
        await self.page.fill('input[name="session[username_or_email]"]', email)
        await self.page.fill('input[name="session[password]"]', password)
        await self.page.click('div[data-testid="LoginForm_Login_Button"]')

    async def change_password(self, current_password: str, new_password: str) -> None:
        """Асинхронное изменение пароля Twitter."""
        logger.info("Изменение пароля Twitter")
        await self.navigate('https://twitter.com/settings/password')
        # Здесь должна быть реализация изменения пароля
        # Примечание: эту часть нужно адаптировать под текущую структуру страницы настроек Twitter

    async def post_random_tweet(self, tweet_text: str) -> None:
        """Асинхронная публикация случайного твита."""
        logger.info(f"Публикация твита: {tweet_text}")
        await self.navigate('https://twitter.com/home')
        await self.page.fill('div[aria-label="Tweet text"]', tweet_text)
        await self.page.click('div[data-testid="tweetButtonInline"]')


class CSVManager:
    @staticmethod
    async def save_data(data: List[Tuple[str, ...]], filename: str = CSV_FILENAME) -> None:
        """Асинхронное сохранение данных аккаунтов в CSV файл."""
        logger.info(f"Сохранение данных в файл {filename}")
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Email", "Password", "First Name", "Last Name", "Backup Email", "Platform"])
            writer.writerows(data)


async def setup_browser():
    """Асинхронная настройка браузера."""
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        headless=False,
        proxy={
            "server": "http://193.169.219.61:50100",  # Proxy server URL
            "username": "quasimodo20042001",          # Proxy username
            "password": "ZHQeZZTIZc"                 # Proxy password
        }
    )
    context = await browser.new_context(
        user_agent=random.choice(USER_AGENTS)
    )
    page = await context.new_page()
    return playwright, browser, context, page



async def run_account_operations():
    """Основная асинхронная функция для работы с Google и Twitter аккаунтами."""
    playwright, browser, context, page = await setup_browser()

    try:
        # Работа с Google аккаунтом
        google_manager = GoogleAccountManager(page)
        google_email = "zhenyaalesich@gmail.com"
        google_password = "Myfassa1999@"
        google_new_password = "124897zzz"
        google_first_name = "John"
        google_last_name = "Doe"

        await google_manager.login(google_email, google_password)
        await google_manager.change_details(google_password, google_new_password, google_first_name, google_last_name)

        # Работа с Twitter аккаунтом
        twitter_manager = TwitterAccountManager(page)
        twitter_email = "twitter_email@gmail.com"
        twitter_password = "witter_current_password"
        twitter_new_password = "twitter_new_password"
        random_tweet = "This is a random tweet!"

        await twitter_manager.login(twitter_email, twitter_password)
        await twitter_manager.change_password(twitter_password, twitter_new_password)
        await twitter_manager.post_random_tweet(random_tweet)

        # Сохранение данных
        data = [
            (
            google_email, google_new_password, google_first_name, google_last_name, 'backup_email@gmail.com', 'Google'),
            (twitter_email, twitter_new_password, 'N/A', 'N/A', 'N/A', 'Twitter')
        ]
        await CSVManager.save_data(data)

    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
    finally:
        await context.close()
        await browser.close()
        await playwright.stop()


if __name__ == "__main__":
    asyncio.run(run_account_operations())
