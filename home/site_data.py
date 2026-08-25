from django.urls import reverse


DESTINATIONS = (
    {
        "name": "Kabul",
        "province": "Kabul",
        "url_name": "states:kabul",
        "image": "image_for_province/kabul.jpeg",
        "summary": "Historic gardens, museums, markets, and the capital's living culture.",
    },
    {
        "name": "Bamyan",
        "province": "Bamyan",
        "url_name": "states:bamyan",
        "image": "image_for_province/bamyan2.jpg",
        "summary": "Cliff landscapes, archaeological heritage, and the lakes of Band-e Amir.",
    },
    {
        "name": "Herat",
        "province": "Herat",
        "url_name": "states:Herat",
        "image": "image_for_province/Herat16.jpg",
        "summary": "Timurid architecture, the citadel, tilework, and western Afghan traditions.",
    },
    {
        "name": "Balkh",
        "province": "Balkh",
        "url_name": "states:balkh",
        "image": "image_for_province/balkh.jpeg",
        "summary": "Ancient Balkh and the Blue Mosque of Mazar-e Sharif.",
    },
    {
        "name": "Nangarhar",
        "province": "Nangarhar",
        "url_name": "states:Nangarhar",
        "image": "image_for_province/nangrher.jpeg",
        "summary": "Jalalabad, green valleys, gardens, and eastern Afghan hospitality.",
    },
    {
        "name": "Kandahar",
        "province": "Kandahar",
        "url_name": "states:Kandahar",
        "image": "image_for_province/kandher.jpg",
        "summary": "Landmarks of Afghan history, traditional bazaars, and the Arghandab valley.",
    },
    {
        "name": "Ghor",
        "province": "Ghor",
        "url_name": "states:Ghor",
        "image": "image_for_province/ghor.jpeg",
        "summary": "Mountain scenery and the UNESCO-listed Minaret of Jam.",
    },
    {
        "name": "Badakhshan",
        "province": "Badakhshan",
        "url_name": "states:Badakhshan",
        "image": "image_for_province/Badakhshan3.jpg",
        "summary": "The Wakhan Corridor, high mountains, and remote communities.",
    },
)


def destination_items():
    return tuple({**item, "url": reverse(item["url_name"])} for item in DESTINATIONS)
