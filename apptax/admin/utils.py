from werkzeug.utils import secure_filename


def taxref_media_file_name(obj, file_data):
  """
  Generate file name
  """
  return secure_filename(f"{obj.taxon.cd_ref}_{file_data.filename}")
