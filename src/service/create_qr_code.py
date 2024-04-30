# import qrcode 
# from PIL import Image

# from fastapi import APIRouter
# from sqlalchemy.orm import Session
# import cloudinary.uploader
# from starlette.responses import FileResponse

# Встановлюємо конфігурацію Cloudinary
cloudinary.config(
    cloud_name="dclrmc6yi", api_key="913556912999135", api_secret="2ZzHdqBkl17s9KN1tkoM0qT0Rwk"
)

# router = APIRouter(prefix="/test", tags=["test"])


# @router.get("/")
# async def create_qr(data: str):
#     user_id = 1
#     image_path = r"src\service\resized_image.jpg"
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=10,
#         border=4,
#     )
#     qr.add_data(data)
#     qr.make(fit=True)
#     qr_img = qr.make_image(fill_color="black", back_color="white")
    
#     # Вставка зображення у центр QR-коду
#     img = Image.open(image_path)
#     img_width, img_height = img.size
#     qr_width, qr_height = qr_img.size
#     pos = ((qr_width - img_width) // 2, (qr_height - img_height) // 2)
#     qr_img.paste(img, pos)
    
#     # Збереження QR-коду з вставленим зображенням
#     qr_img.save("src/service/qr_code.png")
#     return FileResponse("src/service/qr_code.png", media_type='image') 

    