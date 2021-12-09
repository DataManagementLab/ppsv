<h2>Checkliste für Codereviews</h2>

Structure
- [ ] Is the code well-structured, consistent in style, and consistently formatted (Pycharm conventions)?
- [ ] Are there any uncalled or unneeded procedures or any unreachable code?
- [ ] Are there any complex modules that can be broken down into smaller chunks?
- [ ] Can a code be replaced by standard library calls?
- [ ] Are there any leftover stubs or test routines in the code?
- [ ] Are there any uncalled or unneeded procedures or any unreachable code or otherwise unsued items (e.g. variables)?
- [ ] Are there any blocks of repeated code that could be condensed into a single procedure?
- [ ] Are symbolics used rather than “magic number” constants or string constants?
- [ ] Are all variables properly defined with meaningful, consistent, and clear names?

Documentation
- [ ] Is the code clearly and adequately documented with an easy-to-maintain commenting style?
- [ ] Are all comments consistent with the code?

Loops and Branches
- [ ] Are all loops, branches, and logic constructs complete, correct, and properly nested?
- [ ] Are the most common cases tested first in IF- -ELSEIF chains?
- [ ] Are all cases covered in an IF- -ELSEIF or CASE block, including ELSE or DEFAULT clauses?
- [ ] Does every case statement have a default?
- [ ] Are loop termination conditions obvious and invariably achievable?
- [ ] Are indexes or subscripts properly initialized, just prior to the loop?
- [ ] Can any statements that are enclosed within loops be placed outside the loops?
- [ ] Can blocks of IF-ELSE statement be named into function?
- [ ] Does the code in the loop avoid manipulating the index variable or using it upon exit from the loop?

Defensive Programming
- [ ] Are indexes, pointers, and subscripts tested against array, record, or file bounds?
- [ ] Are imported data and input arguments tested for validity and completeness?
- [ ] Are all output variables assigned?
- [ ] Are the correct data operated on in each statement?
- [ ] Are timeouts or error traps used for external device accesses?
- [ ] Are files checked for existence before attempting to access them?
- [ ] Are all files and devices are left in the correct state upon program termination?
- [ ] Do we have test case or unit tests written?

Django
- [ ] Are we storing contents of email outside code?
- [ ] Are we importing specific Classes/Functions from modules from accounts_manager.models import AccountsManager as opposed to from accounts_manager.models import *?
- [ ] Do we have singular application and model names? (E.g. accounts_manager as opposed to accountsmanager)


