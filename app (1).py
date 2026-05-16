import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os  # مكتبة مدمجة للتعامل مع مسارات الملفات في السيرفر
import arabic_reshaper
from bidi.algorithm import get_display

# إعدادات الصفحة
st.set_page_config(page_title="صانع بطاقات المعايدة", layout="centered")

st.title("صانع البطاقات لحملة رفادة")
st.write("قم بتخصيص بطاقتك بإضافة صورتك واسمك، ثم تحميلها مباشرة.")

uploaded_image = st.file_uploader("اختر صورتك الشخصية (اختياري):", type=["png", "jpg", "jpeg"])
user_name = st.text_input("اكتب اسمك الكريم هنا (اختياري):", placeholder="أحمد عبدالله صالح")

if st.button("توليد الكرت بجودة عالية"):
    
    try:
        # قراءة الخلفية
        base_card = Image.open("card_background.png").convert("RGBA")
        card_width, card_height = base_card.size
        
        txt_layer = Image.new("RGBA", base_card.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)
        
        # معالجة وإضافة الصورة الدائرية مع الإطار الذهبي
        if uploaded_image is not None:
            user_img = Image.open(uploaded_image).convert("RGBA")
            size = (240, 240)
            user_img = ImageOps.fit(user_img, size, Image.Resampling.LANCZOS)
            
            mask = Image.new('L', size, 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0) + size, fill=255)
            
            circular_img = Image.new("RGBA", size, (0,0,0,0))
            circular_img.paste(user_img, (0, 0), mask=mask)
            
            x_avatar = (card_width - size[0]) // 2
            y_avatar = 100 
            
            base_card.paste(circular_img, (x_avatar, y_avatar), mask=circular_img)
            
            bounding_box = [x_avatar + 2, y_avatar + 2, x_avatar + size[0] - 2, y_avatar + size[1] - 2]
            draw.ellipse(bounding_box, outline="#d4af37", width=12)
            
        # معالجة الاسم وإصلاح الخط العربي
        if user_name:
            # الحل الأضمن للسيرفر: دمج المسار الحالي مع اسم ملف الخط
            font_filename = "Nazanin.ttf" # تأكدي أن الحروف مطابقة لاسم ملفك في جيت هاب
            font_path = os.path.join(os.getcwd(), font_filename)
            
            try:
                font = ImageFont.truetype(font_path, 40)
            except IOError:
                font = ImageFont.load_default()
                st.warning("تنبيه: لم يتمكن السيرفر من قراءة ملف الخط، تأكدي من رفعه في المجلد الرئيسي وحالة الأحرف.")
            
            reshaped_text = arabic_reshaper.reshape(user_name)
            final_arabic_text = get_display(reshaped_text)
            
            y_text = 725 
            
            left, top, right, bottom = draw.textbbox((0, 0), final_arabic_text, font=font)
            text_width = right - left
            x_text = (card_width - text_width) // 2
            
            draw.text((x_text, y_text), final_arabic_text, fill="white", font=font)
            
        final_card = Image.alpha_composite(base_card, txt_layer).convert("RGB")
        
        st.image(final_card, caption="معاينة الكرت الجاهز", use_container_width=True)
        
        buffer = io.BytesIO()
        final_card.save(buffer, format="PNG")
        byte_im = buffer.getvalue()
        
        st.download_button(
            label="تحميل الكرت كصورة PNG",
            data=byte_im,
            file_name="my_custom_card.png",
            mime="image/png"
        )
        
    except FileNotFoundError:
        st.error("خطأ: لم يتم العثور على صورة card_background.png في السيرفر. تأكدي من تفعيل حساسية الحروف الكبيرة والصغيرة للملف.")
