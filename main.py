import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from io import BytesIO

# إعدادات
NUM_SESSIONS = 8
TRAINING_DAYS = [6, 3]  # أحد = 6، خميس = 3
END_OF_YEAR = datetime(2025, 12, 31)
WEEKDAYS_AR = {6: "أحد", 3: "خميس"}

# عنوان التطبيق
st.set_page_config(page_title="توليد جدول الحضور")
st.title("📅 توليد جدول الحضور لـ ٨ جلسات فقط")
st.write("ارفع ملف Excel يحتوي على ورقة باسم 'اللاعبين' تحتوي على الأعمدة: 'اسم اللاعب' و 'تاريخ البداية'.")

# رفع الملف
uploaded_file = st.file_uploader("📤 رفع ملف Excel", type=["xlsx"])

if uploaded_file:
    try:
        # قراءة الملف
        players_df = pd.read_excel(uploaded_file, sheet_name="اللاعبين")

        # تجهيز البيانات
        players = []
        min_start_date = END_OF_YEAR

        for _, row in players_df.iterrows():
            name = row["اسم اللاعب"]
            start_date = pd.to_datetime(row["تاريخ البداية"], dayfirst=True)
            players.append({"name": name, "start_date": start_date})
            if start_date < min_start_date:
                min_start_date = start_date

        # إنشاء جميع تواريخ التمارين (أحد وخميس فقط)
        all_training_dates = []
        date = min_start_date
        while date <= END_OF_YEAR:
            if date.weekday() in TRAINING_DAYS:
                all_training_dates.append(date)
            date += timedelta(days=1)

        # تجهيز جدول الحضور (٨ جلسات فقط لكل لاعب)
        attendance_rows = []
        for player in players:
            name = player["name"]
            start_date = player["start_date"]
            player_dates = [d for d in all_training_dates if d >= start_date][:NUM_SESSIONS]

            row = {
                "اسم اللاعب": name,
                "تاريخ البداية": start_date.strftime("%d/%m/%Y"),
                "نهاية الاشتراك": player_dates[-1].strftime("%d/%m/%Y") if len(player_dates) == NUM_SESSIONS else ""
            }

            for i, date in enumerate(player_dates):
                col_name = date.strftime("%d/%m/%Y")
                row[col_name] = f"الجلسة {i+1} - {WEEKDAYS_AR.get(date.weekday(), '')}"

            attendance_rows.append(row)

        # تحويل إلى DataFrame
        df = pd.DataFrame(attendance_rows)

        # ترتيب الأعمدة
        fixed_cols = ["اسم اللاعب", "تاريخ البداية", "نهاية الاشتراك"]
        date_cols = sorted(
            [col for col in df.columns if col not in fixed_cols],
            key=lambda x: datetime.strptime(x.split(" ")[0], "%d/%m/%Y")
        )
        df = df[fixed_cols + date_cols]

        # إنشاء ملف Excel في الذاكرة
        output = BytesIO()
        today_str = datetime.today().strftime("%Y-%m-%d")
        file_name = f"حضور_٨_جلسات_{today_str}.xlsx"

        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            players_df.to_excel(writer, sheet_name="اللاعبين", index=False)
            df.to_excel(writer, sheet_name="الحضور المتكرر", index=False)

        # زر التحميل
        st.success("✅ تم إنشاء الملف بنجاح!")
        st.download_button(
            label="📥 تحميل الملف",
            data=output.getvalue(),
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء معالجة الملف: {e}")
