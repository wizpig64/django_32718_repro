from base64 import b64encode

from django.core.files.storage import default_storage
from django.http import HttpResponse

from app.models import EntoMap


def view(request):
    # this view should create 6 files in storage/ento/report-maps/

    with default_storage.open("user_sketch.png") as sketch:
        sketch_uri = f"data:image/png;base64,{b64encode(sketch.read()).decode()}"

    print("creating and saving map for field a")
    fieldmap_a = EntoMap.objects.create(field_id="field_a")
    fieldmap_a.map_background = fieldmap_a.get_background()
    fieldmap_a.set_sketch_datauri(sketch_uri)
    fieldmap_a.compile_maps()
    fieldmap_a.save()

    print("creating and saving map for other")
    fieldmap_b = EntoMap.objects.create(field_id="other")  # use general bg
    fieldmap_b.map_background = fieldmap_b.get_background()
    fieldmap_b.set_sketch_datauri(sketch_uri)
    fieldmap_b.compile_maps()
    fieldmap_b.save()

    return HttpResponse("i did it!")
