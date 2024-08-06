from flask_admin import form


class ImageUploadFieldWithoutDelete(form.ImageUploadField):
    """
    Extension of the `ImageUploadField` class of Flask-Admin.
    This class is used to upload images without the possibility to delete them.

    The widget used to display the field is a custom class `ImageUploadInputWithoutDelete`
    which is a subclass of `ImageUploadInput`.

    Attributes
    ----------
    widget : ImageUploadInputWithoutDelete
        The widget used to display the field.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        class ImageUploadInputWithoutDelete(form.ImageUploadInput):
            """
            Custom widget to display the ImageUploadFieldWithoutDelete.
            It doesn't allow the deletion of images.
            """

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.data_template = (
                    '<div class="image-thumbnail">'
                    " <img %(image)s>"
                    "</div>"
                    "<br>"
                    "<input %(file)s>"
                )

        self.widget = ImageUploadInputWithoutDelete()
