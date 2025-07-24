#
# import pandas as pd
# from datetime import datetime, timedelta
#
# # تحميل قائمة اللاعبين من ملف Excel
# input_file = "بيانات_اللاعبين.xlsx"
# players_df = pd.read_excel(input_file, sheet_name="اللاعبين")
#
# # إعدادات
# num_sessions_per_cycle = 8
# training_days = [6, 3]  # أحد = 6، خميس = 3
# end_of_year = datetime(2025, 12, 31)
#
# # تجهيز بيانات اللاعبين
# players = []
# min_start_date = datetime(2025, 12, 31)
#
# for _, row in players_df.iterrows():
#     name = row["اسم اللاعب"]
#     start_date = pd.to_datetime(row["تاريخ البداية"], dayfirst=True)
#     players.append({"name": name, "start_date": start_date})
#     if start_date < min_start_date:
#         min_start_date = start_date
#
# # توليد كل تواريخ الأحد والخميس حتى نهاية 2025
# all_training_dates = []
# date = min_start_date
# while date <= end_of_year:
#     if date.weekday() in training_days:
#         all_training_dates.append(date)
#     date += timedelta(days=1)
#
# # تجهيز جدول الحضور
# attendance_rows = []
# for player in players:
#     name = player["name"]
#     start_date = player["start_date"]
#
#     # تواريخ الجلسات لكل لاعب بداية من تاريخ بدايته
#     player_dates = [d for d in all_training_dates if d >= start_date]
#
#     row = {
#         "اسم اللاعب": name,
#         "تاريخ البداية": start_date.strftime("%d/%m/%Y")
#     }
#
#     for date in all_training_dates:
#         col_name = date.strftime("%d/%m/%Y")
#
#         if date in player_dates:
#             session_index = player_dates.index(date) + 1
#             cycle_number = (session_index - 1) // num_sessions_per_cycle + 1
#             session_number_in_cycle = ((session_index - 1) % num_sessions_per_cycle) + 1
#             row[col_name] = f"الدورة {cycle_number} الجلسة {session_number_in_cycle}"
#         else:
#             row[col_name] = ""
#
#     attendance_rows.append(row)
#
# # تحويل الجدول إلى DataFrame
# df = pd.DataFrame(attendance_rows)
#
# # ترتيب الأعمدة
# fixed_cols = ["اسم اللاعب", "تاريخ البداية"]
# date_cols = sorted([col for col in df.columns if col not in fixed_cols],
#                    key=lambda x: datetime.strptime(x, "%d/%m/%Y"))
# df = df[fixed_cols + date_cols]
#
# # حفظ الملف النهائي
# output_file = "حضور_متكرر_حتى_نهاية_2025.xlsx"
# with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
#     players_df.to_excel(writer, sheet_name="اللاعبين", index=False)
#     df.to_excel(writer, sheet_name="الحضور المتكرر", index=False)
#
# print(f"✅ تم إنشاء الملف: {output_file}")

import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from io import BytesIO

# إعدادات
num_sessions_per_cycle = 8
training_days = [6, 3]  # أحد = 6، خميس = 3
end_of_year = datetime(2025, 12, 31)

st.title("توليد جدول الحضور للتمارين")
st.write("يرجى رفع ملف Excel يحتوي على أسماء اللاعبين وتواريخ بدايتهم.")

uploaded_file = st.file_uploader("رفع ملف Excel", type=["xlsx"])

if uploaded_file:
    try:
        players_df = pd.read_excel(uploaded_file, sheet_name="اللاعبين")

        players = []
        min_start_date = datetime(2025, 12, 31)

        for _, row in players_df.iterrows():
            name = row["اسم اللاعب"]
            start_date = pd.to_datetime(row["تاريخ البداية"], dayfirst=True)
            players.append({"name": name, "start_date": start_date})
            if start_date < min_start_date:
                min_start_date = start_date

        # تواريخ التمارين
        all_training_dates = []
        date = min_start_date
        while date <= end_of_year:
            if date.weekday() in training_days:
                all_training_dates.append(date)
            date += timedelta(days=1)

        attendance_rows = []
        for player in players:
            name = player["name"]
            start_date = player["start_date"]

            player_dates = [d for d in all_training_dates if d >= start_date]

            row = {
                "اسم اللاعب": name,
                "تاريخ البداية": start_date.strftime("%d/%m/%Y")
            }

            for date in all_training_dates:
                col_name = date.strftime("%d/%m/%Y")

                if date in player_dates:
                    session_index = player_dates.index(date) + 1
                    cycle_number = (session_index - 1) // num_sessions_per_cycle + 1
                    session_number_in_cycle = ((session_index - 1) % num_sessions_per_cycle) + 1
                    row[col_name] = f"الدورة {cycle_number} الجلسة {session_number_in_cycle}"
                else:
                    row[col_name] = ""

            attendance_rows.append(row)

        df = pd.DataFrame(attendance_rows)
        fixed_cols = ["اسم اللاعب", "تاريخ البداية"]
        date_cols = sorted([col for col in df.columns if col not in fixed_cols],
                           key=lambda x: datetime.strptime(x, "%d/%m/%Y"))
        df = df[fixed_cols + date_cols]

        # حفظ الملف في الذاكرة
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            players_df.to_excel(writer, sheet_name="اللاعبين", index=False)
            df.to_excel(writer, sheet_name="الحضور المتكرر", index=False)

        st.success("✅ تم إنشاء الملف بنجاح!")
        st.download_button("📥 تحميل الملف", output.getvalue(), file_name="حضور_متكرر_حتى_نهاية_2025.xlsx")

    except Exception as e:
        st.error(f"حدث خطأ: {e}")
