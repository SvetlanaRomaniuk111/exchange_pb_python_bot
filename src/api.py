import requests
from typing import List, Dict, Any


class PrivatBankAPI:
    """Класс для работы с API Приватбанка"""
    
    @staticmethod
    def get_exchange_rates() -> List[Dict[str, Any]]:
        """
        Получает курсы валют с API Приватбанка
        
        Returns:
            List[Dict[str, Any]]: Список словарей с информацией о курсах валют
            
        Raises:
            Exception: В случае ошибки запроса или обработки данных
        """
        try:
            url = "https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка запроса к API Приватбанка: {str(e)}")
        except ValueError as e:
            raise Exception(f"Ошибка при обработке данных: {str(e)}")