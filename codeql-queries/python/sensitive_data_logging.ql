import python

// Find print statements or logger calls containing sensitive data
from FunctionCall logCall, VariableAccess sensitiveData
where
  logCall.getFunc().getName().matches("print") or logCall.getFunc().getName().matches("logger") and
  sensitiveData.getName().matches("author") or sensitiveData.getName().matches("source_url") or sensitiveData.getName().matches("license")
select logCall, "Avoid logging sensitive data (e.g., author, source URL) to protect privacy and attribution."
