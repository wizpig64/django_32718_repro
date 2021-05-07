import os.path
import re
import tempfile
from base64 import b64decode

from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.core.files.storage import default_storage
from django.db import models
from PIL import Image

MAP_SIZE = (230, 210)  # width, height


def report_map_background_path(instance, filename):
    return f"ento/report-maps/{instance.pk}bg{os.path.splitext(filename)[1]}"


def report_map_sketch_path(instance, filename):
    return f"ento/report-maps/{instance.pk}sk{os.path.splitext(filename)[1]}"


def report_map_composite_path(instance, filename):
    return f"ento/report-maps/{instance.pk}{os.path.splitext(filename)[1]}"


class EntoMap(models.Model):
    field_id = models.CharField(max_length=20)
    map_background = models.ImageField(
        upload_to=report_map_background_path,
        verbose_name="map background",
    )
    map_sketch = models.ImageField(
        upload_to=report_map_sketch_path,
        verbose_name="map sketch",
    )
    map_composite = models.ImageField(
        upload_to=report_map_composite_path,
        height_field="map_height",
        width_field="map_width",
        verbose_name="map composite",
        help_text="The map background and sketch are composited together into this while saving.",
    )
    map_height = models.PositiveSmallIntegerField(null=True, default=MAP_SIZE[1])
    map_width = models.PositiveSmallIntegerField(null=True, default=MAP_SIZE[0])

    class Meta:
        verbose_name = "field map"
        verbose_name_plural = "field maps"

    def get_background(self):
        """Returns a file object holding the default areamap for this field."""
        for name in [
            f"ento/field-maps/{self.field_id}.png",
            "ento/field-maps/general.png",
        ]:
            try:
                return ImageFile(
                    default_storage.open(name),
                    # name=os.path.basename(name),  # needed with 2.2.21+
                )
            except FileNotFoundError:
                pass

    def set_sketch_datauri(self, uri):
        """Creates a ContentFile object from a base64-encoded datauri.

        For example: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA
            AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO
            9TXL0Y4OHwAAAABJRU5ErkJggg=='

        """
        data = re.compile(r"base64,(.*)").search(uri).group(1)
        self.map_sketch = ContentFile(b64decode(data), name="sketch.png")

    def compile_maps(self):
        if self.map_background and self.map_sketch:
            # Flatten together into map_composite
            composite = Image.new("RGBA", MAP_SIZE, (255, 255, 255, 255))
            background = Image.open(self.map_background).convert("RGBA")
            sketch = Image.open(self.map_sketch).convert("RGBA")
            composite.paste(background, mask=background)
            composite.paste(sketch, mask=sketch)
            # Save to a temp file
            composite_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            composite.save(composite_file, format="png")
            composite_file.close()
            # Save to the field's storage
            self.map_composite = ImageFile(
                open(composite_file.name, "rb"),
                # name=os.path.basename(composite_file.name),  # needed with 2.2.21+
            )
            # (this temp file gets removed with a post-save signal)
            self._trash_later = composite_file.name
            print("compile done")
