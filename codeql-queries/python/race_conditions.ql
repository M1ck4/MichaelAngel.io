import python

// Detect variables accessed in a ThreadPoolExecutor without a lock
from VariableAccess var, FunctionCall exec
where
  exec.getFunc().getName() = "ThreadPoolExecutor" and
  var.getEnclosingCallable() = exec.getEnclosingCallable() and
  not var.getEnclosingCallable().getBody().toString().matches("%with lock:%")
select var, "Variable access in multithreaded context without lock."
