import streamlit as st
import pandas as pd
import requests
from datetime import date, datetime

HISTORY_FILE = "price_history.csv"

def save_price_history(flights, origin, destination, flight_date):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    history = []

    for _, row in flights.iterrows():
        history.append({
            "Дата поиска": now,
            "Откуда": origin,
            "Куда": destination,
            "Дата вылета": str(flight_date),
            "Авиакомпания": row["Авиакомпания"],
            "Цена": row["Цена"],
            "Валюта": row["Валюта"]
        })

    new_data = pd.DataFrame(history)

    try:
        old_data = pd.read_csv(HISTORY_FILE)
        new_data = pd.concat([old_data, new_data], ignore_index=True)
    except FileNotFoundError:
        pass

    new_data.to_csv(HISTORY_FILE, index=False)

st.set_page_config(
    page_title="AviaSaver",
    page_icon="✈️",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #F4F8FC;
    color: #243447;
}
.stApp p, .stApp label, .stApp span,
.stApp h1, .stApp h2, .stApp h3 {
    color: #243447;
}
h1 {
    color: #1769AA !important;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.title("✈️ AviaSaver")
st.markdown(
    "<p style='text-align:center;color:#526579;'>"
    "Find your flight. Save your money.</p>",
    unsafe_allow_html=True
)

st.write(
    "Находите авиабилеты и сравнивайте предложения авиакомпаний."
)

st.divider()
st.header("🔎 Поиск авиабилетов")

cities = {
    "Москва (MOW)": "MOW",
    "Ашхабад (ASB)": "ASB",
    "Стамбул (IST)": "IST",
    "Париж (PAR)": "PAR",
    "Лондон (LON)": "LON"
}

col1, col2 = st.columns(2)

with col1:
    origin_name = st.selectbox("Откуда", list(cities.keys()))

with col2:
    destination_name = st.selectbox("Куда", list(cities.keys()))

col3, col4 = st.columns(2)

with col3:
    flight_date = st.date_input(
        "Дата вылета",
        min_value=date.today()
    )

with col4:
    passengers = st.number_input(
        "Количество пассажиров",
        min_value=1,
        max_value=9,
        value=1
    )

if st.button("🔍 Найти авиабилеты", type="primary"):

    origin = cities[origin_name]
    destination = cities[destination_name]

    if origin == destination:
        st.warning("Выберите разные города вылета и назначения.")

    else:
        try:
            api_key = st.secrets["DUFFEL_API_KEY"]

            url = "https://api.duffel.com/air/offer_requests"

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Duffel-Version": "v2",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            payload = {
                "data": {
                    "slices": [
                        {
                            "origin": origin,
                            "destination": destination,
                            "departure_date": str(flight_date)
                        }
                    ],
                    "passengers": [
                        {"type": "adult"}
                        for _ in range(int(passengers))
                    ],
                    "cabin_class": "economy"
                }
            }

            with st.spinner("Ищем авиабилеты..."):
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=60
                )

            if response.status_code in (200, 201):
                result = response.json()
                offers = result.get("data", {}).get("offers", [])

                st.success(
                    f"Результаты поиска: {origin_name} — "
                    f"{destination_name}"
                )

                if offers:
                    flights = []

                    for offer in offers:
                        slices = offer.get("slices", [])
                        segments = []

                        for flight_slice in slices:
                            segments.extend(
                                flight_slice.get("segments", [])
                            )

                        airline_names = []

                        for segment in segments:
                            carrier = segment.get(
                                "operating_carrier", {}
                            )
                            name = carrier.get("name")

                            if name and name not in airline_names:
                                airline_names.append(name)

                        airline = (
                            ", ".join(airline_names)
                            or offer.get("owner", {}).get("name", "Не указана")
                        )

                        stops = max(0, len(segments) - len(slices))

                        flights.append({
                            "Авиакомпания": airline,
                            "Цена": float(offer.get("total_amount", 0)),
                            "Валюта": offer.get("total_currency", ""),
                            "Пересадки": stops
                        })

                    df = pd.DataFrame(flights)
                    df = df.sort_values("Цена")

                    st.subheader("✈️ Найденные предложения")
                    st.dataframe(df, use_container_width=True)

                    cheapest = df.iloc[0]

                    st.info(
                        f"Самое дешёвое предложение: "
                        f"{cheapest['Цена']:.2f} "
                        f"{cheapest['Валюта']}"
                    )

                else:
                    st.info(
                        "Duffel не вернул предложений. "
                        "Попробуйте другую дату или направление."
                    )

                st.caption(
                    "AviaSaver использует Duffel API. "
                    "Результаты тестового режима могут быть демонстрационными."
                )

            else:
                st.error(
                    f"Ошибка Duffel API: {response.status_code}"
                )
                st.write(response.text[:1000])

        except KeyError:
            st.error(
                "Не найден ключ DUFFEL_API_KEY. "
                "Проверьте настройки Secrets в Streamlit."
            )

        except requests.exceptions.Timeout:
            st.error("Сервер Duffel не ответил вовремя. Попробуйте ещё раз.")

        except requests.exceptions.RequestException:
            st.error("Не удалось подключиться к Duffel. Проверьте интернет.")

        except Exception as e:
            st.error(f"Произошла ошибка: {e}")

st.divider()

st.markdown(
    "<center>AviaSaver © 2026 | Учебный проект</center>",
    unsafe_allow_html=True
)

