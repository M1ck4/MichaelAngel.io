import python

// Check if metadata fields (author, license, source URL) are present in image processing code
from FunctionCall imageLoad, VariableAccess metadata
where
  imageLoad.getFunc().getName().matches("load_image") and
  metadata.getName().matches("author") or
  metadata.getName().matches("license") or
  metadata.getName().matches("source_url")
select imageLoad, "Ensure image retains necessary Creative Commons metadata (author, license, source URL)."
