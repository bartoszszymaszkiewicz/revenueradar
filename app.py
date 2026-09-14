import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Revenue Radar",
    page_icon="📡",
    layout="wide"
)

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def money(value):
    return f"{value:,.0f} PLN".replace(",", " ")

def safe_read_csv(path):
    if Path(path).exists():
        return pd.read_csv(path)
    return pd.DataFrame()

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("📡 Revenue Radar")
st.caption(
    "Demo na danych syntetycznych. Kwoty są estymacją opartą na danych historycznych."
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

customer_tasks = safe_read_csv("customer_tasks.csv")
opportunities = safe_read_csv("opportunities.csv")
winback = safe_read_csv("winback.csv")
cross_sell = safe_read_csv("cross_sell.csv")

tabs = st.tabs(
    [
        "📈 Ponowne zamówienia",
        "♻️ Win-back",
        "🧩 Cross-sell"
    ]
)

# ==================================================
# TAB 1 - REORDER
# ==================================================

with tabs[0]:

    st.subheader("Dzisiejsze szanse sprzedażowe")

    if customer_tasks.empty or opportunities.empty:
        st.warning("Brakuje plików customer_tasks.csv lub opportunities.csv.")
    else:
        total_clients = len(customer_tasks)
        total_revenue = customer_tasks["total_expected_revenue"].sum()

        high_confidence_opportunities = opportunities[
            opportunities["confidence_score_v2"] >= 75
        ]

        total_products = high_confidence_opportunities["product_id"].nunique()

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Klienci z wysokim priorytetem",
            total_clients
        )

        col2.metric(
            "Wykryty potencjał sprzedaży",
            money(total_revenue)
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
                f"{row['customer_name']} — {money(row['total_expected_revenue'])}"
            ):

                st.write(
                    f"**Liczba produktów:** {int(row['products_count'])}"
                )

                st.write(
                    f"**Wiarygodność rekomendacji:** {row['avg_confidence']:.1f}%"
                )

                client_opportunities = opportunities[
                    (
                        opportunities["customer_id"] == row["customer_id"]
                    )
                    &
                    (
                        opportunities["confidence_score_v2"] >= 75
                    )
                ].sort_values(
                    "expected_revenue",
                    ascending=False
                )

                st.markdown("### Dlaczego system to sugeruje?")

                for _, item in client_opportunities.iterrows():

                    status = item["opportunity_status_v2"]

                    if status == "due_soon":
                        timing_text = "zbliża się do typowego terminu zakupu"
                    elif status == "overdue":
                        timing_text = "przekroczył typowy termin zakupu"
                    else:
                        timing_text = "wykazuje sygnał ponownego zakupu"

                    st.write(
                        f"**{item['product_name']}** — klient {timing_text}. "
                        f"Kupował ten produkt **{int(item['purchase_count'])} razy**, "
                        f"średnio co **{item['avg_interval_days']:.0f} dni**. "
                        f"Od ostatniego zakupu minęło "
                        f"**{int(item['days_since_last_purchase'])} dni**. "
                        f"Przewidywana wartość: **{money(item['expected_revenue'])}**. "
                        f"Wiarygodność: **{item['confidence_score_v2']:.0f}%**."
                    )

                st.markdown("### Zadanie handlowe")

                st.selectbox(
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
                    "Rekomendacja: skontaktuj się z klientem i przygotuj "
                    "propozycję ponownego zamówienia."
                )

# ==================================================
# TAB 2 - WIN-BACK
# ==================================================

with tabs[1]:

    st.subheader("Klienci i produkty do odzyskania")

    if winback.empty:
        st.warning("Brakuje pliku winback.csv.")
    else:
        total_winback = len(winback)
        total_recovery_value = winback["expected_recovery_value"].sum()
        winback_clients = winback["customer_id"].nunique()

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Wykryte przypadki Win-back",
            total_winback
        )

        col2.metric(
            "Potencjalna wartość odzyskania",
            money(total_recovery_value)
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

            cycle_multiple = (
                item["days_since_last_purchase"] / item["avg_interval_days"]
                if item["avg_interval_days"] > 0
                else 0
            )

            with st.expander(
                f"{item['customer_name']} — "
                f"{item['product_name']} — "
                f"{money(item['expected_recovery_value'])}"
            ):

                st.markdown("### Co wykrył system?")

                st.write(
                    f"Klient kupował **{item['product_name']}** "
                    f"**{int(item['purchase_count'])} razy**."
                )

                st.write(
                    f"Typowy cykl zakupowy wynosił około "
                    f"**{item['avg_interval_days']:.0f} dni**."
                )

                st.write(
                    f"Od ostatniego zakupu minęło już "
                    f"**{int(item['days_since_last_purchase'])} dni**, czyli około "
                    f"**{cycle_multiple:.1f}× typowego cyklu zakupowego**."
                )

                st.write(
                    f"Historyczna wartość typowego zakupu wynosi około "
                    f"**{money(item['expected_recovery_value'])}**."
                )

                st.write(
                    f"Wiarygodność rekomendacji Win-back: "
                    f"**{item['winback_confidence']:.0f}%**."
                )

                st.markdown("### Rekomendacja")

                st.warning(
                    "Klient wypadł z wcześniejszego cyklu zakupowego. "
                    "Sprawdź przyczynę braku kolejnych zamówień i rozważ "
                    "kontakt w celu odzyskania sprzedaży."
                )

                st.selectbox(
                    "Status",
                    [
                        "Do sprawdzenia",
                        "Kontakt zaplanowany",
                        "Kontakt wykonany",
                        "Klient odzyskany",
                        "Brak potencjału"
                    ],
                    key=f"winback_{item['customer_id']}_{item['product_id']}"
                )

# ==================================================
# TAB 3 - CROSS-SELL
# ==================================================

with tabs[2]:

    st.subheader("Możliwości sprzedaży uzupełniającej")

    if cross_sell.empty:
        st.warning(
            "Brakuje pliku cross_sell.csv. "
            "Wygeneruj go w Colabie i dodaj do repozytorium."
        )
    else:
        total_cross_sell = len(cross_sell)
        cross_sell_clients = cross_sell["customer_id"].nunique()
        total_cross_sell_value = cross_sell["expected_cross_sell_value"].sum()

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Wykryte możliwości Cross-sell",
            total_cross_sell
        )

        col2.metric(
            "Klienci z potencjałem",
            cross_sell_clients
        )

        col3.metric(
            "Szacowana wartość możliwości",
            money(total_cross_sell_value)
        )

        st.divider()
        st.subheader("Najważniejsze propozycje")

        cross_sell_sorted = cross_sell.sort_values(
            "cross_sell_score",
            ascending=False
        )

        for _, item in cross_sell_sorted.head(100).iterrows():

            with st.expander(
                f"{item['customer_name']} — "
                f"{item['target_product_name']} — "
                f"{money(item['expected_cross_sell_value'])}"
            ):

                st.markdown("### Dlaczego system to sugeruje?")

                st.write(
                    f"Klient kupował **{item['source_product_name']}** "
                    f"**{int(item['source_purchase_count'])} razy**, "
                    f"ale nigdy nie kupił produktu "
                    f"**{item['target_product_name']}**."
                )

                st.write(
                    f"Wśród klientów kupujących **{item['source_product_name']}**, "
                    f"około **{item['pair_confidence']:.0f}%** kupowało również "
                    f"**{item['target_product_name']}**."
                )

                st.write(
                    f"Liczba innych klientów potwierdzających ten wzorzec: "
                    f"**{int(item['supporting_customers'])}**."
                )

                st.write(
                    f"Szacowana wartość pierwszego zakupu: "
                    f"**{money(item['expected_cross_sell_value'])}**."
                )

                st.write(
                    f"Wiarygodność rekomendacji: "
                    f"**{item['cross_sell_confidence']:.0f}%**."
                )

                st.markdown("### Rekomendacja")

                st.success(
                    "Dodaj produkt do kolejnej oferty lub zapytaj klienta, "
                    "czy jest zainteresowany produktem uzupełniającym."
                )

                st.selectbox(
                    "Status",
                    [
                        "Nowe",
                        "Do sprawdzenia",
                        "Oferta przygotowana",
                        "Oferta wysłana",
                        "Sprzedane",
                        "Brak zainteresowania"
                    ],
                    key=f"crosssell_{item['customer_id']}_{item['target_product_id']}"
                )
