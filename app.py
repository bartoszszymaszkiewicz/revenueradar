import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Revenue Radar",
    layout="wide"
)

st.title("Revenue Radar")
st.caption("Demo na danych syntetycznych")

customer_tasks = pd.read_csv("customer_tasks.csv")
opportunities = pd.read_csv("opportunities.csv")

# KPI
total_clients = len(customer_tasks)

total_revenue = customer_tasks[
    "total_expected_revenue"
].sum()

total_products = opportunities[
    opportunities["confidence_score_v2"] >= 75
]["product_id"].nunique()

col1, col2, col3 = st.columns(3)

col1.metric(
    "Klienci z wysokim priorytetem",
    total_clients
)

col2.metric(
    "Wykryty potencjał sprzedaży",
    f"{total_revenue:,.0f} PLN"
)

col3.metric(
    "Produkty do ponownej oferty",
    total_products
)

st.divider()

st.subheader("Najważniejsze zadania")

for _, row in customer_tasks.sort_values(
    "total_expected_revenue",
    ascending=False
).iterrows():

    with st.expander(
        f"{row['customer_name']} — "
        f"{row['total_expected_revenue']:,.0f} PLN"
    ):

        st.write(
            f"**Liczba produktów:** "
            f"{int(row['products_count'])}"
        )

        st.write(
            f"**Średni confidence:** "
            f"{row['avg_confidence']:.1f}%"
        )

        client_opportunities = opportunities[
            (
                opportunities["customer_id"]
                == row["customer_id"]
            )
            &
            (
                opportunities["confidence_score_v2"]
                >= 75
            )
        ].sort_values(
            "expected_revenue",
            ascending=False
        )

        st.markdown(
            "### Dlaczego system to sugeruje?"
        )

        for _, item in client_opportunities.iterrows():

            status = item[
                "opportunity_status_v2"
            ]

            if status == "due_soon":
                timing_text = (
                    "zbliża się do typowego "
                    "terminu zakupu"
                )

            elif status == "overdue":
                timing_text = (
                    "przekroczył typowy "
                    "termin zakupu"
                )

            else:
                timing_text = (
                    "wykazuje sygnał "
                    "ponownego zakupu"
                )

            st.write(
                f"**{item['product_name']}** — "
                f"klient {timing_text}. "
                f"Przewidywana wartość: "
                f"**{item['expected_revenue']:,.0f} PLN**, "
                f"confidence: "
                f"**{item['confidence_score_v2']:.0f}%**."
            )

        st.markdown("### Zadanie handlowe")

        status_option = st.selectbox(
            "Status",
            [
                "Nowe",
                "W trakcie",
                "Oferta wysłana",
                "Wygrane",
                "Odrzucone"
            ],
            key=f"status_{row['customer_id']}"
        )

        st.info(
            "Rekomendacja: skontaktuj się z klientem "
            "i przygotuj propozycję ponownego zamówienia."
        )
