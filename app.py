import streamlit as st
from supabase import create_client, Client

# Konfiguracja połączenia z Supabase
# Na Streamlit Cloud dodaj te dane do "Secrets"
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(URL, KEY)

st.set_page_config(page_title="Zarządzanie Produktami", layout="wide")

st.title("📦 System Zarządzania Produktami i Kategoriami")

# --- FUNKCJE POMOCNICZE ---
def get_categories():
    response = supabase.table("kategorie").select("*").execute()
    return response.data

def get_products():
    # Pobieramy produkty wraz z nazwą kategorii (join)
    response = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
    return response.data

# --- SIDEBAR: DODAWANIE ---
st.sidebar.header("Dodaj Nowe Dane")

# Formularz Kategorii
with st.sidebar.expander("Dodaj Kategorię"):
    kat_nazwa = st.text_input("Nazwa Kategorii")
    kat_opis = st.text_area("Opis Kategorii")
    if st.button("Zapisz Kategorię"):
        if kat_nazwa:
            supabase.table("kategorie").insert({"nazwa": kat_nazwa, "opis": kat_opis}).execute()
            st.success("Dodano kategorię!")
            st.rerun()

# Formularz Produktu
with st.sidebar.expander("Dodaj Produkt"):
    kategorie = get_categories()
    kat_opcje = {k['nazwa']: k['id'] for k in kategorie}
    
    prod_nazwa = st.text_input("Nazwa Produktu")
    prod_liczba = st.number_input("Liczba", min_value=0, step=1)
    prod_cena = st.number_input("Cena", min_value=0, step=1)
    wybrana_kat = st.selectbox("Kategoria", options=list(kat_opcje.keys()))
    
    if st.button("Zapisz Produkt"):
        if prod_nazwa and wybrana_kat:
            nowy_produkt = {
                "nazwa": prod_nazwa,
                "liczba": prod_liczba,
                "cena": prod_cena,
                "kategoria_id": kat_opcje[wybrana_kat]
            }
            supabase.table("produkty").insert(nowy_produkt).execute()
            st.success("Dodano produkt!")
            st.rerun()

# --- GŁÓWNY PANEL: WYŚWIETLANIE I USUWANIE ---
tab1, tab2 = st.tabs(["Produkty", "Kategorie"])

with tab1:
    st.subheader("Lista Produktów")
    produkty = get_products()
    if produkty:
        for p in produkty:
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 2, 1])
            col1.write(f"**{p['nazwa']}**")
            col2.write(f"{p['liczba']} szt.")
            col3.write(f"{p['cena']} zł")
            col4.write(f"📁 {p['kategorie']['nazwa'] if p['kategorie'] else 'Brak'}")
            if col5.button("Usuń", key=f"prod_{p['id']}"):
                supabase.table("produkty").delete().eq("id", p['id']).execute()
                st.rerun()
    else:
        st.info("Brak produktów w bazie.")

with tab2:
    st.subheader("Lista Kategorii")
    kategorie_lista = get_categories()
    if kategorie_lista:
        for k in kategorie_lista:
            col1, col2, col3 = st.columns([3, 4, 1])
            col1.write(f"**{k['nazwa']}**")
            col2.write(f"{k['opis']}")
            if col3.button("Usuń", key=f"kat_{k['id']}"):
                try:
                    supabase.table("kategorie").delete().eq("id", k['id']).execute()
                    st.rerun()
                except Exception:
                    st.error("Nie można usunąć kategorii, która zawiera produkty!")
    else:
        st.info("Brak kategorii w bazie.")
