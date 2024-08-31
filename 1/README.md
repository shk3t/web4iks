## Запись вебинара

https://a.teleboss.ru/play/b218962a-d681-43e4-acda-5cbc3b648b0a

<br />

## Требования

- Python (использовался 3.12.5)
- Docker (использовался 27.1.2)

## Установка

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: `.venv\Scripts\activate`
pip install -r requirements.txt

docker build -t mp_db db
docker run --name mp_db -e POSTGRES_PASSWORD=pass -p 2345:5432 -d mp_db
```

## Запуск

```bash
python main.py
```

## Если сложности с Докером

Можно импортировать данные из `.csv` при помощи следующего кода:

```python
def get_nomenclatures() -> DataFrame:
    return pd.read_csv("csv/nomenclatures.csv")

# То же самое для остальных таблиц
```
