import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Revenue Radar",
    layout="wide"
)

st.title("Revenue Radar")
st.caption("Demo na danych syntetycznych")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

customer_tasks = pd.read_csv("customer_tasks.csv")
opportunities = pd.read_csv("opportunities.csv")
winback = pd.read_csv("winback.csv")

# --------------------------------------------------
# MAIN TABS
# --------------------------------------------------

tab1, tab2 = st.tabs(
    [
        "📈 Reorder Opportunities",
        "♻️ Win-back"
    ]
)

# ==================================================
# TAB 1 - REORDER
# ==================================================

with tab1:

    st.subheader("Dzisiejsze szanse sprzedażowe")

    total_clients = len(customer_tasks)

    total_revenue = customer_tasks[
        "total_expected_revenue"
    ].sum()

    high_confidence_opportunities = opportunities[
        opportunities["confidence_score_v2"] >= 75
    ]

    total_products = (
        high_confidence_opportunities["product_id"]
        .nunique()
    )

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
                    f"Kupował ten produkt "
                    f"**{int(item['purchase_count'])} razy**, "
                    f"średnio co "
                    f"**{item['avg_interval_days']:.0f} dni**. "
                    f"Od ostatniego zakupu minęło "
                    f"**{int(item['days_since_last_purchase'])} dni**. "
                    f"Przewidywana wartość: "
                    f"**{item['expected_revenue']:,.0f} PLN**. "
                    f"Confidence: "
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
                key=f"reorder_status_{row['customer_id']}"
            )

            st.info(
                "Rekomendacja: skontaktuj się z klientem "
                "i przygotuj propozycję ponownego zamówienia."
            )

# ==================================================
# TAB 2 - WIN-BACK
# ==================================================

with tab2:

    st.subheader("Klienci i produkty do odzyskania")

    total_winback = len(winback)

    total_recovery_value = (
        winback["expected_recovery_value"].sum()
    )

    winback_clients = (
        winback["customer_id"]
        .nunique()
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Wykryte przypadki Win-back",
        total_winback
    )

    col2.metric(
        "Potencjalna wartość odzyskania",
        f"{total_recovery_value:,.0f} PLN"
    )

    col3.metric(
        "Klienci do ponownego kontaktu",
        winback_clients
    )

    st.divider()

    st.subheader("Najważniejsze możliwości odzyskania")

    winback_sorted = winback.sort_values(
        "expected_recovery_value",
        ascending=False
    )

    for _, item in winback_sorted.iterrows():

        with st.expander(
            f"{item['customer_name']} — "
            f"{item['product_name']} — "
            f"{item['expected_recovery_value']:,.0f} PLN"
        ):

            st.markdown("### Co wykrył system?")

            st.write(
                f"Klient kupował "
                f"**{item['product_name']}** "
                f"**{int(item['purchase_count'])} razy**."
            )

            st.write(
                f"Typowy cykl zakupowy wynosił około "
                f"**{item['avg_interval_days']:.0f} dni**."
            )

            st.write(
                f"Od ostatniego zakupu minęło już "
                f"**{int(item['days_since_last_purchase'])} dni**."
            )

            st.write(
                f"Historyczna wartość typowego zakupu wynosi około "
                f"**{item['expected_recovery_value']:,.0f} PLN**."
            )

            st.write(
                f"Confidence Win-back: "
                f"**{item['winback_confidence']:.0f}%**."
            )

            st.markdown("### Rekomendacja")

            st.warning(
                "Klient wypadł z wcześniejszego cyklu zakupowego. "
                "Sprawdź przyczynę braku kolejnych zamówień i "
                "rozważ kontakt w celu odzyskania sprzedaży."
            )

            status_option = st.selectbox(
                "Status",
                [
                    "Do sprawdzenia",
                    "Kontakt zaplanowany",
                    "Kontakt wykonany",
                    "Klient odzyskany",
                    "Brak potencjału"
                ],
                key=(
                    f"winback_"
                    f"{item['customer_id']}_"
                    f"{item['product_id']}"
                )
            )
