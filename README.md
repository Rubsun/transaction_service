
# 💰 Transaction Service

Микросервис для учёта и анализа пользовательских транзакций с категоризацией, лимитами и системой уведомлений.

---

## 🐳 Инструкция по запуску проекта

### 🔧 Предварительные требования

Перед запуском убедитесь, что на вашей машине установлены:

- Docker: https://www.docker.com/get-started  
- Docker Compose (если используется отдельно): https://docs.docker.com/compose/install/

---

### ⚙️ Конфигурация

**Файл `configs/db.env`**

Должен содержать переменные окружения для Postgres, например:

POSTGRES_USER=postgres  
POSTGRES_PASSWORD=postgres  
POSTGRES_DB=postgres

**Файл `app.docker.toml`**

Файл конфигурации приложения. Путь до него указывается в переменной окружения `PROFILE_SERVICE_CONFIG_PATH`.

---

### 🚀 Запуск

1. Соберите и запустите контейнеры:

docker compose up --build

2. Проверьте, что сервисы запустились:

- FastAPI-сервис: http://localhost:8000/docs  
- Prometheus: http://localhost:9090  
- Grafana: http://localhost:3000  
  Логин: admin  
  Пароль: admin

---

### 📮 Postman-коллекция

В проекте доступна готовая коллекция для тестирования всех основных сценариев:

- Импорт транзакций  
- Проверка категоризации  
- Проверка дневного и недельного лимита  
- Получение пользовательской статистики

Файл коллекции: `postman/TransactionService_Full.postman_collection.json`

Импортируйте в Postman через:  
Файл → Импорт → Выбрать файл → Импортировать коллекцию

---

### 🧼 Остановка и очистка

Остановить контейнеры:

docker compose down

Удалить контейнеры, образы и тома:

docker compose down --volumes --rmi all

---