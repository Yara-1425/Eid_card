import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io

# إعدادات الصفحة
st.set_page_config(page_title="صانع بطاقات المعايدة", layout="centered")

st.title("صانع البطاقات لحملة رفادة")
st.write("قم بتخصيص بطاقتك بإضافة صورتك واسمك، ثم تحميلها مباشرة.")

# 1. رفع الصورة وإدخال الاسم من المستخدم
uploaded_image = st.file_uploader("اختر صورتك الشخصية (اختياري):", type=["png", "jpg", "jpeg"])
user_name = st.text_input("اكتب اسمك الكريم هنا (اختياري):", placeholder="الاسم الكريم")

# زر المعالجة والتوليد
if st.button("توليد الكرت بجودة عالية"):
    
    try:
        # 2. فتح خلفية الكرت الأصلية
        # تأكد من وجود ملف باسم card_background.png في نفس المجلد
        base_card = Image.open("card_background.png").convert("RGBA")
        card_width, card_height = base_card.size
        
        # إنشاء طبقة للرسم فوق الكرت
        txt_layer = Image.new("RGBA", base_card.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)
        
        # 3. معالجة وإضافة الصورة الدائرية (إذا تم رفعها)
        if uploaded_image is not None:
            user_img = Image.open(uploaded_image).convert("RGBA")
            
            # تحديد مقاس الصورة الدائرية (مثلاً 250x250 بكسل)
            size = (250, 250)
            user_img = ImageOps.fit(user_img, size, Image.Resampling.LANCZOS)
            
            # صنع قناع دائري (Circle Mask) قص الصورة بشكل دائري
            mask = Image.new('L', size, 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0) + size, fill=255)
            
            # دمج القناع مع صورة المستخدم
            circular_img = Image.new("RGBA", size, (0,0,0,0))
            circular_img.paste(user_img, (0, 0), mask=mask)
            
            
            # حساب إحداثيات المنتصف في الأعلى لوضع الصورة
            # يمكنك تعديل رقم 120 (الارتفاع من الأعلى) ليناسب كرتك بالضبط
            x_avatar = (card_width - size[0]) // 2
            y_avatar = 120 
            
            base_card.paste(circular_img, (x_avatar, y_avatar), mask=circular_img)
            
        # 4. إضافة الاسم داخل المستطيل البني (إذا تم كتابته)
        if user_name:
            # محاولة تحميل خط Nazanin، وإذا لم يوجد يتم استخدام الخط الافتراضي
            try:
                # حجم الخط 40 (يمكنك تكبيره أو تصغيره)
                font = ImageFont.truetype("NAZANIN.TTF", 40)
            except IOError:
                font = ImageFont.load_default()
                st.warning("لم يتم العثور على ملف خط Nazanin.ttf، تم استخدام الخط الافتراضي.")
            
            # تحديد مكان المستطيل البني (الإحداثيات التقريبية للمنتصف)
            # يمكنك تعديل رقم 580 (الارتفاع من الأعلى ليكون داخل المستطيل البني تماماً)
            y_text = 725
            
            # حساب عرض النص لجعله في المنتصف تماماً
            left, top, right, bottom = draw.textbbox((0, 0), user_name, font=font)
            text_width = right - left
            x_text = (card_width - text_width) // 2
            
            # رسم النص باللون الأبيض
            draw.text((x_text, y_text), user_name, fill="white", font=font)
            
        # دمج الطبقات معاً
        final_card = Image.alpha_composite(base_card, txt_layer).convert("RGB")
        
        # 5. عرض النتيجة للمستخدم في الموقع
        st.image(final_card, caption="معاينة الكرت الجاهز", use_container_width=True)
        
        # تحويل الصورة إلى بايتات لتمكين تحميلها
        buffer = io.BytesIO()
        final_card.save(buffer, format="PNG")
        byte_im = buffer.getvalue()
        
        # زر التحميل
        st.download_button(
            label="تحميل الكرت كصورة PNG",
            data=byte_im,
            file_name="my_custom_card.png",
            mime="image/png"
        )
        
    except FileNotFoundError:
        st.error("رجاءً تأكد من تسمية الصورة الأصلية بـ card_background.png ووضعها في نفس المجلد مع الكود.")
