from django.test import TestCase
from decimal import Decimal
from .services import execute_transfer
from .models import TransactionModel
from wallets.models import CardModel
from users.models import UserModel


# Не забудь импорты моделей кошельков, юзеров и своей функции execute_transfer

class TransferServiceTests(TestCase):
    def setUp(self):
        self.sender = UserModel.objects.create(username='asan', password='asanchik', phone='+996700102030')
        self.receiver = UserModel.objects.create(username='uson', password='usonchik', phone='+996500102030')
        self.sender_wallet = CardModel.objects.create(
            owner=self.sender, balance=Decimal('500.0000'))
        self.receiver_wallet = CardModel.objects.create(owner=self.receiver, balance=Decimal('0.0000'))
        
        # Шаг 1: Подготовка
        # Джанго запускает эту функцию перед каждым тестом.
        # Создай тут двух фейковых юзеров и два кошелька для них.
        # Отправителю (например, self.sender_wallet) дай на баланс 1000.
        # Получателю (self.receiver_wallet) дай 0.

    def test_successful_transfer_changes_balances(self):
        # Шаг 2: Действие
        # Вызови функцию execute_transfer, попробуй перевести 100 сомов.
        execute_transfer(self.sender_wallet, self.receiver_wallet, Decimal('300.0000'))
        
        # Обновляем данные из БД после перевода (это обязательно, иначе Питон будет помнить старые цифры)
        self.sender_wallet.refresh_from_db()
        self.receiver_wallet.refresh_from_db()

        # Шаг 3: Проверка
        self.assertEqual(TransactionModel.objects.all().last().status, "OK")
        self.assertEqual(self.receiver_wallet.balance, Decimal('300.0000'))
        self.assertEqual(self.sender_wallet.balance, Decimal('195.5000'))
    def test_insufficient_balance_raising(self):
        with self.assertRaises(ValueError):
            execute_transfer(self.sender_wallet, self.receiver_wallet, Decimal('500.0000'))
        # Используй self.assertEqual(что_получилось, что_ожидаем)
        # 1. Проверь баланс получателя (должен стать 100)
        # 2. Проверь баланс отправителя (посчитай, сколько должно остаться с учетом комиссии 1.5%)
        # 3. Проверь, создался ли чек в TransactionModel (можно через TransactionModel.objects.count())