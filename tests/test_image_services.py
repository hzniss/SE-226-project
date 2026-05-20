from services.image_service import generate_cover_image, get_placeholder_image

image = generate_cover_image(
    cover_prompt="rainy seaside at night, melancholic mood",
    genre="Indie"
)

if image:
    image.show()
    image.save("test_cover.png")
    print("Image successfully created")
else:
    fallback = get_placeholder_image()
    fallback.show()
    print("Fallback.")