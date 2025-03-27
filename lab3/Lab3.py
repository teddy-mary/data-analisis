import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Завантаження даних з CSV (кешоване)
@st.cache_data
def load_from_file():
    return pd.read_csv("all_vhi.csv")

df_replace = load_from_file()

area_names = {
    1: 'Вінницька', 2: 'Волинська', 3: 'Дніпропетровська', 4: 'Донецька', 5: 'Житомирська',
    6: 'Закарпатська', 7: 'Запорізька', 8: 'Івано-Франківська', 9: 'Київська', 10: 'Кіровоградська',
    11: 'Луганська', 12: 'Львівська', 13: 'Миколаївська', 14: 'Одеська', 15: 'Полтавська',
    16: 'Рівенська', 17: 'Сумська', 18: 'Тернопільська', 19: 'Харківська', 20: 'Херсонська',
    21: 'Хмельницька', 22: 'Черкаська', 23: 'Чернівецька', 24: 'Чернігівська', 25: 'Республіка Крим'
}

# Назва додатку
st.title("Лабораторна №3")

# Параметри діапазонів
index_options = ["VCI", "TCI", "VHI"]
min_year, max_year = int(df_replace["Year"].min()), int(df_replace["Year"].max())
min_week, max_week = int(df_replace["Week"].min()), int(df_replace["Week"].max())

if "index" not in st.session_state:
    st.session_state["index"] = "VCI"
if "area" not in st.session_state:
    st.session_state["area"] = list(area_names.values())[0]
if "weeks" not in st.session_state:
    st.session_state["weeks"] = (min_week, max_week)
if "years" not in st.session_state:
    st.session_state["years"] = (min_year, max_year)
if "sort_asc" not in st.session_state:
    st.session_state["sort_asc"] = False
if "sort_desc" not in st.session_state:
    st.session_state["sort_desc"] = False

# 9 - 2 колонки: фільтри та результат
col1, col2 = st.columns([1, 2])

# Колонка з фільтрами (інтерактивними елементами)
with col1:
    st.subheader("Фільтри")

    # 1 - dropdown список, який дозволить обрати часовий ряд VCI, TCI, VHI
    selected_index = st.selectbox("Оберіть часовий ряд", index_options, key="index")

    # 2 - dropdown список, який дозволить вибрати область
    selected_area = st.selectbox("Оберіть область", list(area_names.values()), index=0, key="area")
    area_id = list(area_names.keys())[list(area_names.values()).index(selected_area)]

    # 3 - slider, який дозволить зазначити інтервал тижнів
    week_range = st.slider("Інтервал тижнів", min_week, max_week, key="weeks")

    # 4 - slider, який дозволить зазначити інтервал років
    year_range = st.slider("Інтервал років", min_year, max_year, key="years")

    # 8 - два checkbox для сортування даних за зростанням та спаданням значень VCI, TCI або VHI
    asc = st.checkbox("Сортувати за зростанням", key="sort_asc")
    desc = st.checkbox("Сортувати за спаданням", key="sort_desc")

    # 5 - button для скидання всіх фільтрів і повернення до початкового стану даних
    if st.button("Скинути фільтри"):
        st.session_state.clear()
        st.rerun()

# Фільтрація даних за вибраними параметрами
filtered_df = df_replace[
    (df_replace["Region_ID"] == area_id) &
    (df_replace["Year"].between(year_range[0], year_range[1])) &
    (df_replace["Week"].between(week_range[0], week_range[1]))
].copy()

# 8 - Сортування
if asc and not desc:
    filtered_df = filtered_df.sort_values(by=selected_index, ascending=True)
elif desc and not asc:
    filtered_df = filtered_df.sort_values(by=selected_index, ascending=False)
elif asc and desc:
    st.warning("!!!! Увімкнені обидва сортування — сортування не застосовано.")

# Колонка з графіками та таблицею
with col2:
    # 6 - три вкладки для відображення таблиці з відфільтрованими даними, відповідного до неї графіка та графіка порівняння даних по областях
    tab1, tab2, tab3 = st.tabs(["Таблиця", "Графік області", "Порівняння по областях"])

    with tab1:
        st.write("Відфільтровані дані:")
        filtered_df["Область"] = filtered_df["Region_ID"].map(area_names)
        st.dataframe(filtered_df[["Область", "Year", "Week", selected_index]])

with tab2:
    st.write("Графік індексу для обраної області")
    if not filtered_df.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=filtered_df, x="Week", y=selected_index, hue="Year", ax=ax)
        ax.set_title(f"{selected_index} для {selected_area}")
        ax.set_ylabel(selected_index)
        ax.set_xlabel("Week")
        st.pyplot(fig)
    else:
        st.warning("Немає даних для побудови графіка.")

    with tab3:
        st.write("Порівняння по регіонах")
        compare_df = df_replace[
            (df_replace["Year"].between(year_range[0], year_range[1])) &
            (df_replace["Week"].between(week_range[0], week_range[1]))
        ]
        avg_values = compare_df.groupby("Region_ID")[selected_index].mean().reset_index()
        avg_values["Область"] = avg_values["Region_ID"].map(area_names)

        fig2, ax2 = plt.subplots(figsize=(14, 7))
        sns.barplot(data=avg_values, x="Область", y=selected_index, ax=ax2)
        ax2.set_title(f"Середнє значення {selected_index} по регіонах")
        ax2.set_ylabel(f"{selected_index}")
        ax2.set_xlabel("Область")
        ax2.tick_params(axis='x', rotation=45)
        st.pyplot(fig2)