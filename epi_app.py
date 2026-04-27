import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap, Fullscreen
import pandas as pd
from epi_model import EpidemicModel # استدعاء كلاس الحسابات

class EpidemicApp:
    def __init__(self):
        st.set_page_config(page_title="نظام الاستخبارات الوبائية", layout="wide")
        self.model = EpidemicModel()

    def render_sidebar(self):
        with st.sidebar:
            st.header("إعدادات النموذج")
            beta = st.slider("معدل العدوى (Beta)", 0.1, 1.0, 0.5)
            gamma = st.slider("معدل الشفاء (Gamma)", 0.01, 0.5, 0.1)
            lockdown = st.select_slider("مستوى الإجراءات الاحترازية", 
                                       options=["بدون", "خفيف", "متوسط", "عالي", "كلي"])
            impact_map = {"بدون": 0.0, "خفيف": 0.2, "متوسط": 0.45, "عالي": 0.7, "كلي": 0.9}
            return beta, gamma, lockdown, impact_map[lockdown]

    def run(self):
        st.title("المركز الوطني لتحليل البيانات الوبائية - العراق")
        beta, gamma, lockdown_label, impact_val = self.render_sidebar()
        
        # جلب البيانات والحسابات من كلاس الموديل
        df_raw = self.model.load_data()
        df, loss, saved = self.model.calculate(df_raw, beta, gamma, impact_val)

        tab1, tab2 = st.tabs(["الخريطة الحرارية الجغرافية", "غرفة التحليل والقرار"])

        with tab1:
            m = folium.Map(location=[33.3, 44.0], zoom_start=6, tiles='OpenStreetMap')
            # قطر ديناميكي يتأثر بالحظر
            dyn_radius = 25 * (1 - impact_val) + 5
            heat_data = [[r['latitude'], r['longitude'], r['infected_total']] for _, r in df.iterrows() if r['infected_total'] > 0]
            if heat_data:
                HeatMap(heat_data, radius=dyn_radius, blur=15).add_to(m)
            Fullscreen().add_to(m)
            st_folium(m, width=1100, height=600)

        with tab2:
            st.subheader("تحليل الأثر الاقتصادي والاستراتيجي")
            c1, c2 = st.columns(2)
            with c1:
                st.info("الأثر المادي")
                st.metric("التكلفة المالية اليومية", f"${loss:,.0f}", delta=f"الحظر: {lockdown_label}", delta_color="inverse")
            with c2:
                st.success("الأثر الصحي")
                st.metric("أرواح تم إنقاذها", f"{saved:,} شخص")

            st.markdown("---")
            st.markdown("<h4 style='text-align: center;'>ميزان المفاضلة البصري (مقارنة النسب)</h4>", unsafe_allow_html=True)
            
            l_col, m_col, r_col = st.columns([1, 3, 1])
            with m_col:
                loss_p = (loss / 100_000_000) * 100
                lives_max = (df['infected_total'].sum() * 0.08) if df['infected_total'].sum() > 0 else 1
                lives_p = (saved / lives_max) * 100
                st.bar_chart(pd.DataFrame({'الفئة': ['الخسارة المادية', 'الأرواح المنقذة'], 'القيمة': [loss_p, lives_p]}).set_index('الفئة'))

            st.markdown("---")
            st.subheader("تفاصيل انتشار الوباء حسب المحافظة")
            df_display = df[['name', 'population', 'infected_total', 'risk_score']].copy()
            df_display.columns = ['المحافظة', 'عدد السكان', 'إجمالي الإصابات', 'درجة الخطورة %']
            st.dataframe(df_display.sort_values(by='درجة الخطورة %', ascending=False), use_container_width=True)

            # قسم لغة R المدمج داخل tab2 بشكل صحيح
            st.markdown("---") 
            st.subheader("التحليل الإحصائي المتقدم (بواسطة لغة R)")
            
            col_r1, col_r2 = st.columns([2, 1])
            with col_r1:
                # تأكدي أن صورة r_plot.png موجودة في نفس مجلد المشروع
                try:
                    st.image("r_plot.png", caption="رسم بياني تم إنتاجه بمكتبة ggplot2 في R", use_container_width=True)
                except:
                    st.warning("⚠️ لم يتم العثور على ملف r_plot.png في المجلد.")
            with col_r2:
                st.write("""
                **لماذا استخدمنا R هنا؟**
                * للتحقق من صحة التوزيع الإحصائي للسكان.
                * لضمان دقة النتائج قبل عرضها في واجهة البايثون.
                * لاستخدام قوة مكتبة ggplot2 في التمثيل البياني الأكاديمي.
                """)

if __name__ == "__main__":
    app = EpidemicApp()
    app.run()