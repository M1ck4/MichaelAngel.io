import python

// Detect unclosed file resources
from FunctionCall openFile, Variable fileVar
where
  openFile.getFunc().getName() = "open" and
  fileVar = openFile.getAnArgument(0) and
  not fileVar.getEnclosingCallable().getBody().toString().matches("%close()")
select openFile, "Potential unclosed file resource."
