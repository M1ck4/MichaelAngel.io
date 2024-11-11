import python

// Find cases where attribution information (author, license) is modified
from VariableAccess attributionVar
where
  attributionVar.getName().matches("author") or
  attributionVar.getName().matches("license") and
  attributionVar.isWriteAccess()
select attributionVar, "Avoid modifying attribution information to maintain data integrity."
