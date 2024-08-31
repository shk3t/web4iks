from typing import Literal
import pandas as pd
from pandas import DataFrame
from datetime import datetime, UTC


DB_URL = "postgresql://postgres:pass@localhost:2345/postgres"
METRICS = ["amount", "revenue", "profit"]


def get_nomenclatures() -> DataFrame:
    return pd.read_sql("nomenclature", DB_URL)


def get_sizes() -> DataFrame:
    return pd.read_sql("size", DB_URL)


def get_sales() -> DataFrame:
    return pd.read_sql("sale", DB_URL)


def get_stocks() -> DataFrame:
    return pd.read_sql("stock", DB_URL)


def get_lost_profits(
    start_date: datetime,
    end_date: datetime,
    order_by: Literal["amount", "revenue", "profit"] | None = None,
) -> DataFrame:
    nomenclatures = get_nomenclatures()
    sizes = get_sizes()
    sales = get_sales()
    stocks = get_stocks()
    sizes = sizes.rename(columns={"id": "size_id"})
    nomenclatures = nomenclatures.rename(columns={"id": "nomenclature_id"})
    sales = pd.merge(sales, sizes, on="size_id")
    stocks = pd.merge(stocks, sizes, on="size_id")

    sales["profit"] = sales["price"] - sales["cost"]
    sales["date"] = pd.to_datetime(sales["date"])
    stocks["date"] = pd.to_datetime(stocks["date"])

    sales = sales[(sales["date"] > start_date) & (sales["date"] < end_date)]
    stocks = stocks[(stocks["date"] > start_date) & (stocks["date"] < end_date)]

    # Спрос: Среднедневные продажи товара A
    # size_id, mean_amount, mean_price, mean_profit
    sales_agg = sales.groupby(
        ["nomenclature_id", "size_id", pd.Grouper(key="date", freq="D")]
    ).agg(
        amount=pd.NamedAgg("id", "count"),
        revenue=pd.NamedAgg("price", "sum"),
        profit=pd.NamedAgg("profit", "sum"),
    )
    sales_agg = sales_agg.groupby(["size_id"]).mean()

    # Отсутствие предложения: Сегодня на складах товара A нет в наличии
    # size_id, lost_days
    stocks_agg = (
        stocks.groupby(
            ["nomenclature_id", "size_id", pd.Grouper(key="date", freq="D")]
        )[["quantity"]]
        .sum()
        .query("quantity == 0")
    )
    stocks_agg = stocks_agg.groupby(["size_id"]).agg(
        lost_days=pd.NamedAgg("quantity", "count")
    )

    # result = Кол-во дней отсутствия на складах * Среднедневную стоимость
    # size_id, lost_days, mean_amount ...
    result = pd.merge(sales_agg, stocks_agg, on="size_id")
    result = result[METRICS].mul(result["lost_days"], axis=0)
    result[METRICS] = result[METRICS].round(2)

    # Агрегируем по size_id и nomenclature_id
    result = pd.merge(result, sizes, on="size_id")
    result = pd.merge(result, nomenclatures, on="nomenclature_id")
    result = result.rename(columns={"value": "size"})

    if order_by:
        result = result.sort_values(order_by, ascending=False)

    # title, amount, revenue, profit
    return result[["title", "size", *METRICS]]


if __name__ == "__main__":
    lost_profits = get_lost_profits(
        start_date=datetime(2024, 5, 1, tzinfo=UTC),
        end_date=datetime(2024, 5, 31, tzinfo=UTC),
        order_by="profit",
    )
    # lost_profits.to_excel("lost_profits.xlsx", index=False)
    lost_profits.to_csv("lost_profits.csv", index=False)
