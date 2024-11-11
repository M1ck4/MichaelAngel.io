import python

// Select loop statements containing calls to database functions
from FunctionCall dbCall, LoopStmt loop
where dbCall.getFunc().getName().matches("execute") and dbCall = loop.getAChild()
select dbCall, "Redundant database call within a loop, consider moving it outside the loop if possible."
