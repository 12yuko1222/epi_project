import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap, Fullscreen
import pandas as pd
from epi_model import EpidemicModel 

class EpidemicApp:
    def __init__(self):
        st.set_page_config(page_title="المنصة الوطنية للرصد والتنبؤ الوبائي", layout="wide")
        self.model = EpidemicModel()

    def render_sidebar(self):
        with st.sidebar:
            st.header("إعدادات النموذج")
            # شرح المتغيرات برمجياً
            beta = st.slider("معدل العدوى (Beta)", 0.1, 1.0, 0.5, help="يمثل سرعة انتقال العدوى بين الأفراد")
            gamma = st.slider("معدل الشفاء (Gamma)", 0.01, 0.5, 0.1, help="يمثل سرعة تعافي المصابين")
            lockdown = st.select_slider("مستوى الإجراءات الاحترازية", 
                                       options=["بدون", "خفيف", "متوسط", "عالي", "كلي"])
            
            # إضافة الـ Legend تحت السلايدر مباشرة لتوضيح الألوان
            st.markdown("---")
            st.markdown("### 🗺️ مفتاح الرصد الجغرافي")
            st.markdown("""
            <div style="padding: 12px; border-radius: 10px; border: 1px solid #457b9d; background-color: #f8f9fa;">
                <p style="margin: 0; font-size: 14px;">
                    <strong style="color: #e63946;">🔴 أحمر:</strong> بؤر انتشار (خطر عالي)<br>
                    <strong style="color: #f4a261;">🟠 برتقالي:</strong> انتشار نشط (متوسط)<br>
                    <strong style="color: #2a9d8f;">🟢 أخضر:</strong> مستويات آمنة (استقرار)
                </p>
            </div>
            <p style="font-size: 11px; color: gray; margin-top: 5px;">* تعتمد الألوان على كثافة الإصابات بالنسبة للسكان.</p>
            """, unsafe_allow_html=True)
            st.markdown("---")
            
            impact_map = {"بدون": 0.0, "خفيف": 0.2, "متوسط": 0.45, "عالي": 0.7, "كلي": 0.9}
            return beta, gamma, lockdown, impact_map[lockdown]

    def run(self):
        st.title("المنصة الوطنية للرصد والتنبؤ الوبائي - العراق")
        beta, gamma, lockdown_label, impact_val = self.render_sidebar()
        
        df_raw = self.model.load_data()
        df, loss, saved = self.model.calculate(df_raw, beta, gamma, impact_val)

        tab1, tab2 = st.tabs(["ميكانيكية الانتشار وبؤر الإصابة", "لوحة التقييم الاستراتيجي ودعم القرار"])

        with tab1:
            # رسم الخريطة التفاعلية
            m = folium.Map(location=[33.3, 44.0], zoom_start=6, tiles='OpenStreetMap')
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
            st.markdown("<h4 style='text-align: center;'>ميزان الاستجابة: المكتسبات البشرية مقابل الأعباء المالية</h4>", unsafe_allow_html=True)
            
            l_col, m_col, r_col = st.columns([1, 3, 1])
            with m_col:
                loss_p = (loss / 100_000_000) * 100
                lives_max = (df['infected_total'].sum() * 0.08) if df['infected_total'].sum() > 0 else 1
                lives_p = (saved / lives_max) * 100
                st.bar_chart(pd.DataFrame({'المؤشر': ['الأعباء المالية', 'المكتسبات البشرية'], 'النسبة': [loss_p, lives_p]}).set_index('المؤشر'))

            st.markdown("---")
            st.subheader("سجل الرقابة الصحية والتهديدات النسبية")
            df_display = df[['name', 'population', 'infected_total', 'risk_score']].copy()
            df_display.columns = ['المحافظة', 'عدد السكان', 'إجمالي الإصابات', 'درجة الخطورة %']
            st.dataframe(df_display.sort_values(by='درجة الخطورة %', ascending=False), use_container_width=True)

            st.markdown("---") 
            st.subheader("التحليل الإحصائي المتقدم (بواسطة لغة R)")
            
            col_r1, col_r2 = st.columns([2, 1])
            with col_r1:
                try:
                    st.image("r_plot.png", caption="التحليل الوصفي المولد بواسطة R", use_container_width=True)
                except:
                    st.warning("⚠️ ملف r_plot.png غير موجود.")
            with col_r2:
                st.write("""
                **تكامل النمذجة الإحصائية (R Framework):**
                * **المصادقة (Validation):** إخضاع البيانات لاختبارات التوزيع لضمان موثوقية التنبؤات.
                * **الدقة الرياضية:** استخدام خوارزميات R المتقدمة لمعالجة المتغيرات السكانية.
                * **التمثيل الأكاديمي:** استخراج تقارير بصرية عالية الدقة تواكب المعايير العالمية.
                """)

if __name__ == "__main__":
    app = EpidemicApp()
    app.run()