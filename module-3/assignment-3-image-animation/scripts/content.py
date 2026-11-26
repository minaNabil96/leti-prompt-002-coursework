"""Single source of truth for table content and prompts used in the report."""

SETTINGS = [
    {
        "work": "Портрет (S1)",
        "service": "Polza.ai, bytedance/seedance-2-mini, image-to-video",
        "speed": "5 с, 24 кадра/с (121 кадр)",
        "smooth": "высокая: движение нарастает без рывков",
        "depth": "минимальная: мимика и лёгкий поворот головы",
        "moved": ("веки (моргание), голова (наклон), губы (улыбка), плечи (дыхание); "
                  "кадр постепенно приближается"),
        "wrong": ("незапрошенный наезд камеры: к финалу плечи обрезаны, "
                  "черты лица слегка плывут"),
    },
    {
        "work": "Пейзаж (S2)",
        "service": "Polza.ai, bytedance/seedance-2-mini, image-to-video",
        "speed": "5 с, 24 кадра/с (121 кадр)",
        "smooth": "средняя: вода и облака идут ровно, отражения опережают воду",
        "depth": "средняя: два элемента — вода и облака",
        "moved": ("облака (дрейф и смена формы), вода (рябь и перестройка отражений); "
                  "деревья почти статичны"),
        "wrong": ("белая точка-артефакт в левом верхнем углу к концу ролика; "
                  "деревья не качаются, хотя были в промпте"),
    },
    {
        "work": "Свободная: «Звёздная ночь» (S3)",
        "service": "Polza.ai, bytedance/seedance-2-mini, image-to-video",
        "speed": "5 с, 24 кадра/с (121 кадр)",
        "smooth": "низкая: вихри и звёзды смещаются скачками",
        "depth": "максимальная: небо, звёзды, кипарис, огни деревни",
        "moved": ("вихри неба (вращение), звёзды и луна (рост и мерцание), "
                  "кипарис (раскачивание), огни деревни (мерцание); "
                  "композиция плывёт и приближается"),
        "wrong": ("звёзды дублируются и меняют размер, у правого края появляется "
                  "белая царапина, исходная рама картины обрезана"),
    },
]

PROMPTS = {
    "source_01": ("A professional portrait of a young woman with short dark hair, soft natural "
                  "lighting, neutral grey background, looking directly at the camera, "
                  "photorealistic, high detail"),
    "source_02": ("A serene mountain lake at sunset with gentle pink clouds, calm water with "
                  "subtle reflections, pine trees on the shore, warm golden light, "
                  "photorealistic landscape"),
    "animation_01": ("Subtle animation: the woman blinks once slowly, tilts her head slightly "
                     "to the right, and forms a gentle smile. Minimal movement, natural "
                     "breathing motion."),
    "animation_02": ("Clouds drift slowly from left to right, water surface ripples gently with "
                     "reflections, pine branches sway in a light breeze. Two moving elements "
                     "only, medium intensity."),
    "animation_03": ("Maximum dynamic animation: the swirling sky rotates and pulses, stars "
                     "twinkle brightly, the cypress tree sways dramatically, village lights "
                     "flicker, the moon glows intensely. Full transformation."),
}

SOURCE_URL = ("https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/"
              "Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/"
              "1280px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg")
