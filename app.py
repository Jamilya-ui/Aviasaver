import streamlit as st
import pandas as pd

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
.stApp div, .stApp h1, .stApp h2,
.stApp h3 {
    color: #243447;
}
h1 {
    color: #1769AA !important;
    text-align: center;
}
.subtitle {
    text-align: center;
    color: #526579 !important;
    font-size: 18px;
}
[data-baseweb="input"] input {
    color: #243447 !important;
}
</style>
""", unsafe_allow_html=True)



st.title("✈️ AviaSaver")
st.markdown(
    '<p class="subtitle">Find your flight. Save your money.</p>',
    unsafe_allow_html=True
)

st.write(
    "Находите выгодные авиабилеты "
    "и сравнивайте предложения авиакомпаний."
)

st.divider()

st.header("🔎 Поиск авиабилетов")

col1, col2 = st.columns(2)

with col1:
    origin = st.text_input("Откуда", placeholder="Например, Москва")

with col2:
    destination = st.text_input("Куда", placeholder="Например, Стамбул")

col3, col4 = st.columns(2)

with col3:
    flight_date = st.date_input("Дата вылета")

with col4:
    passengers = st.number_input(
        "Количество пассажиров",
        min_value=1,
        max_value=9,
        value=1
    )

if st.button("🔍 Найти авиабилеты", type="primary"):

    if not origin.strip() or not destination.strip():
        st.warning("Пожалуйста, заполните города вылета и назначения.")

    elif origin.strip().lower() == destination.strip().lower():
        st.warning("Города вылета и назначения должны отличаться.")

    else:
        flights = pd.DataFrame([
            {
                "Авиакомпания": "Turkish Airlines",
                "Цена": 18500,
                "Валюта": "RUB",
                "Пересадки": 0
            },
            {
                "Авиакомпания": "Aeroflot",
                "Цена": 21300,
                "Валюта": "RUB",
                "Пересадки": 1
            },
            {
                "Авиакомпания": "Pegasus Airlines",
                "Цена": 16200,
                "Валюта": "RUB",
                "Пересадки": 1
            }
        ])

        flights = flights.sort_values("Цена")

        st.success(
            f"Результаты: {origin} — {destination}. "
            f"Дата: {flight_date}. Пассажиров: {passengers}."
        )

        st.subheader("✈️ Найденные предложения")
        st.dataframe(flights, use_container_width=True)

        st.info(
            "Это демонстрационные данные для учебного проекта. "
            "Они не являются реальными предложениями авиакомпаний."
        )

st.divider()

st.markdown(
    "<center>AviaSaver © 2026 | Учебный проект</center>",
    unsafe_allow_html=True
)
