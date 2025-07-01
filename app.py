import streamlit as st
import sqlite3
import pandas as pd
import altair as alt
from datetime import date

# Połączenie z bazą danych SQLite
conn = sqlite3.connect("sales.db")
c = conn.cursor()

# Tworzenie tabeli sales (jeśli nie istnieje)
c.execute('''
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product TEXT,
    quantity INTEGER,
    unit_price REAL,
    date TEXT,
    latitude REAL,
    longitude REAL
)
''')
conn.commit()

# Nagłówek aplikacji
st.title("📊 Aplikacja Sprzedażowa - Streamlit")

# Form do dodania nowej sprzedaży
st.subheader("➕ Dodaj nową sprzedaż")

with st.form("sales_form"):
    product = st.selectbox("Produkt", ["Laptop", "Telefon", "Monitor", "Tablet"])
    quantity = st.number_input("Ilość", min_value=1, value=1)
    unit_price = st.number_input("Cena jednostkowa", min_value=1.0, value=1000.0)
    sale_date = st.date_input("Data sprzedaży", value=date.today())

    st.markdown("#### 🌍 Lokalizacja sprzedaży")
    city = st.selectbox("Wybierz miasto", {
        "Warszawa": (52.2297, 21.0122),
        "Kraków": (50.0647, 19.9450),
        "Wrocław": (51.1079, 17.0385),
        "Poznań": (52.4064, 16.9252),
        "Gdańsk": (54.3520, 18.6466)
    })
    lat, lon = city

    submitted = st.form_submit_button("Dodaj")

    if submitted:
        c.execute("INSERT INTO sales (product, quantity, unit_price, date, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?)",
                  (product, quantity, unit_price, sale_date.isoformat(), lat, lon))
        conn.commit()
        st.success("✅ Sprzedaż została dodana!")
        st.balloons()

# Pobranie danych z bazy do DataFrame
df = pd.read_sql_query("SELECT * FROM sales", conn)

# Filtrowanie danych po produkcie
st.subheader("📄 Lista sprzedaży")
selected_product = st.selectbox("Filtruj po produkcie", ["Wszystkie"] + df["product"].unique().tolist())
if selected_product != "Wszystkie":
    df = df[df["product"] == selected_product]

st.dataframe(df)

# Wykres 1: Sprzedaż dzienna (ilość * cena)
st.subheader("📈 Sprzedaż dzienna (wartość)")
df["value"] = df["quantity"] * df["unit_price"]
chart1 = alt.Chart(df).mark_bar().encode(
    x='date:T',
    y='value:Q',
    tooltip=['product', 'quantity', 'unit_price', 'value']
).properties(width=700)
st.altair_chart(chart1, use_container_width=True)

# Wykres 2: Suma sprzedanych produktów wg typu
st.subheader("📊 Liczba sprzedanych produktów wg typu")
chart2 = alt.Chart(df).mark_arc().encode(
    theta=alt.Theta(field="quantity", type="quantitative"),
    color=alt.Color(field="product", type="nominal"),
    tooltip=['product', 'quantity']
)
st.altair_chart(chart2, use_container_width=True)

# Mapa sprzedaży
st.subheader("🗺️ Mapa lokalizacji sprzedaży")
map_data = df[["latitude", "longitude"]].dropna()
st.map(map_data)

# Zamknięcie połączenia
conn.close()
