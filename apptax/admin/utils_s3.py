from flask_admin.form.upload import FileUploadField

from apptax.taxonomie.filemanager import FILEMANAGER


class S3FileUploadField(FileUploadField):
    """
    Inherits from flask-admin FileUploadField, to allow file uploading
    to Amazon S3 (as well as the default local storage).
    """

    _file_manager = None

    def __init__(
        self,
        label=None,
        validators=None,
        storage_type=None,
        namegen=None,
        **kwargs,
    ):
        super(S3FileUploadField, self).__init__(
            label=label, validators=validators, namegen=namegen, **kwargs
        )

        if storage_type and (storage_type != "s3"):
            raise ValueError(
                'Storage type "%s" is invalid, the only supported storage type'
                " (apart from default local storage) is s3." % storage_type
            )

        self.storage_type = storage_type
        self._file_manager = FILEMANAGER

    def _delete_file(self, filename):
        try:
            self._file_manager.remove_file(filename)
        except Exception:
            pass

    def _save_file(self, temp_file, filename):
        temp_file.seek(0)
        self._file_manager.upload_file(temp_file, filename=filename)
        return filename
