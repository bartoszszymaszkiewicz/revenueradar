
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Revenue Radar",
    layout="wide"
)

st.title("Revenue Radar")
st.subheader("Dzisiejsze szanse sprzedażowe")

customer_tasks = pd.read_csv("customer_tasks.csv")
opportunities = pd.read_csv("opportunities.csv")

total_clients = len(customer_tasks)
total_revenue = customer_tasks["total_expected_revenue"].sum()

col1, col2 = st.columns(2)

col1.metric(
    "Klienci z wysokim priorytetem",
    total_clients
)

col2.metric(
    "Wykryty potencjał sprzedaży",
    f"{total_revenue:,.0f} PLN"
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
            f"**Liczba produktów:** {int(row['products_count'])}"
        )

        st.write(
            f"**Średni confidence:** "
            f"{row['avg_confidence']:.1f}%"
        )

        client_opportunities = opportunities[
            opportunities["customer_id"] == row["customer_id"]
        ].sort_values(
            "expected_revenue",
            ascending=False
        )

        st.dataframe(
            client_opportunities[
                [
                    "product_name",
                    "opportunity_status_v2",
                    "expected_revenue",
                    "confidence_score_v2",
                    "recommendation"
                ]
            ],
            use_container_width=True
        )
