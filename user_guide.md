# User Guide

This guide provides a basic overview of all the features of the Admins and Teachers webpages of the PPSV.

## Model

### Slot

A topic can contain multiple slots. Every slot has a minimum and a maximum number of students that can be assigned to it.
A topic having n slots means that the topic can be assigned to n distinct groups of students.

### Application

An application describes that a student or a group of student wants to apply for a topic of a course.
Every application has an associated priority. A priority of 1 means that the topic is the most preferred topic of the student / the group.

### Collection

A collection is a set of applications that are grouped together. 
Every collection belongs to exactly one student or one group of students.
A student or a group of students can have multiple collections.

### Assignment

An assignment corresponds to a specific slot of a topic and a specific application of a collection.
The existence of an assignment means that the application of the collection is assigned to the slot of the topic.
Only one application of a collection can be assigned to a slot of a topic at any time.
It can happen that there are collections without any assignment.
If the maximum number of students in a slot is high enough, it can happen that two groups of student are assigned to the same slot.

## Home Page

If you are logged in as a staff or admin member you are automatically redirected to the home page. You can also access it by clicking on the "Assignment Home Page" button in the navigation bar at the top or the title of the webpage.
The page can also be reached at `.../home/`.

### Filter

On the top left you can see the filter.
It filters the statistic and score by the provided settings.
When switching to the Assignment Page all filter settings are kept.

### Statistics

On the bottom left of the screen you can see the statistics of the current assignments.
It is always associated with the filter selected above and the term selected within the dropdown menu.
The statistic shows how many students and how many groups are assigned to the application with priority 1,2,3...
The students count includes the students that applied for a topic as a group and vice versa (a single student will be counted as a group containing one student).
The group and student count is calculated per collection which means that a student with two collections will be counted twice.

### Unfulfilled Collections

In the middle of the screen you can see all unfulfilled Collections.
The list is based on the current active term.
Aside from the group, the corresponding collection is also shown.
By clicking on a displayed item you get redirected to the Assignment Page with the collection of the group shown on the right.

### Slots with Errors

On the right of the screen you can see all slots that have an errors.
The list is based on the current active term.
Usually these are only slots where students are assigned, but they are less than the minimum number of students required by the slot.
It also includes slots where the maximum number of students is exceeded, or slots that include student without an application for the slot, etc.
The last two scenarios should not happen in practice, but if they do, they are displayed here.
By clicking on a displayed item you get redirected to the Assignment Page with the slot opened.
You can also clear a slot, which will delete all applications from this slot, and should resolve any errors that occur. However, this action can not be reversed

### Export

At the top right you can see the export button which will download two csv file containing the current applications and assignments.
You can use these files to manually assign students or groups to slots.
It will always export the current active term.
On the left of it you can choose the faculty for which you want to export the data.
Locked slots and locked applications (locking will be explained later) will not be included in the exported files.

### Import

The import is located left to the export. You can select a file to import by clicking the button.
The file must be a '.csv' file and an adaptation of the beforehand exported 'export_assignments.csv' file.
The separator of the csv must either be a ',' or a ';'.
The slots and applications being locked should not be changed in the time between export and import.

## Assignment Page

If you are logged in as a staff member you can access the assignment page by clicking on the "Assignment Page" button in the navigation bar at the top while on the home page.
The page can also be reached at `.../assignment/`.

### Topics

On the left you can see all topics of the current active term sorted by the associated course.
By clicking on a topic you can open it and see all slots, assignments and applications of the topic.
By clicking on the "X" button above the applications or the topic again you can close it.
By clicking on a course you can hide its topics.
By entering a query into the searchbar above you can filter for topics and courses whose names contain the entered search term.

### Filter

Next to the searchbar you can see the filter button.
After pressing it you can select the filter settings and close it again by clicking on the "X" or anywhere in the background.
Afterwards only topics that match the selected filters will be shown.
Filter settings are kept for 5 Days.

### Drag and Drop

After opening a topic you can drag and drop applications from the list on the right (Applications) to the slots on the left (Assignments).
You can also drag and drop applications from one slot to another.
These changes will be automatically stored in the database.
After every change you will see a feedback on the top of the page.
From left to right the displayed applications contain the following information:
- the tu-ids of the students in the application
- the priority of the application 
- a symbol whether an application of the collection is already assigned (✓), no application is assigned but at least on could be assigned (grid) or no application is assigned and non can be assigned (✖)
- the number of application that can still be assigned / the amount of applications in the collection

### Group Details

The group details are shown on the right after clicking on an application and consist of two lists.
The first one is a list of all tu-ids of the members of the group.
The second one is a list of all applications in the viewed collection, listed by their priority.
The information displayed on the applications are from left to right:
- the priority
- the topic and course name
- the amount of slots of the topic the group can be assigned to ("Free Slots")
An application has a red background if the group can't be assigned to the topic anymore and a green background if the group is assigned to the topic.
Clicking on an application will open the associated topic in the middle

### Statistics

On the bottom right of the screen you can expand the statistics by clicking on it.
It includes the statics and the score from the home page as well as the amount of slots with errors and the amount of collections where no application is assigned ("open applications").
It will get updated with every change of applications and assignments.

### Groups by currently assigned priority

At the bottom of the screen, next to the statistic, you can expand the 'groups by currently assigned priority' by clicking on it.
There you can see all collections of all groups.
They are grouped by the priority of the assigned application of the collection.
You can display different priorities by clicking on the respective number on the left.
The number zero is for collections where no application is assigned.
By clicking on a collection the group details of the collection will be displayed.

### Slots with Errors

next to 'Groups by currently assigned priority' you can expand the 'Slots with Errors' by clicking on it.
The shown view is equivalent to the 'Slots with Errors' view on the home page.

### Locked Slots/assigned applications

At the corner of a slot and on the left side of an assigned application you can click the lock symbol to lock or unlock the respective slot or assigned application.
Slots can only be locked if the required minimum number of students are assigned.
Assigned application can not be dragged into or out of locked slots.
Locked assigned applications can not be dragged out of their slot.
Slots can be locked by an administrator or by the term being finalized. In this case you can't unlock them.

### Assignment settings

Next to the filter button you can find three settings that you can enable or disable by clicking the checkbox next to them.
- When 'Override Slot' is enabled you can assign a group to a slot even if another group is already assigned to the slot and the maximum slot size doesn't allow both groups to be assigned at the same time. 
The group that was previously assigned to the slot will be automatically unassigned. If there are multiple options to switch you will get a dialog with the possible options. (If this is not selected you will always get a dialog to confirm an exchange)
It is only possible to exchange one to one.
- When 'Override Application' is enabled you can assign a group to a slot even if an assignment for an application of the associated collection already exists.
This assignment will then be removed.
- When you open any group information and 'Open first open Application of group' is enabled the topic of the first application in the selected collection of the group that can still be assigned will be opened in the middle.

## Admin Controls

If you are logged in as an administrator you can access the admin controls by clicking on the "Admin Controls" button in the navigation bar at the top while on the home page.
The page can also be reached at `.../admin_functionality/`.

### Start an automatic Assignment with Override

You can start an automatic assignment where the current assignments will be overwritten.
The new assignment will be saved to the database.
Locked slots and locked assigned applications will not be changed by the algorithm.

### Lock and Finalize all Assignments

If there are no errors in the current assignments of the term it can be finalized.
All slots will get locked.
This should only be done if all applications have been assigned for the term.
Note that students are no longer able to access any content, as long as the active term is finalized.

### Unlock all Assignments

The finalisation of the term will be reversed, all slots will get unlocked to their previous state.
This is not possible after Emails got send

### Send Emails

Sends an email to all students that have created at least one application in the current active term.
Emails can only be sent if all Assignments are finalized and locked.
For every term the emails can only be sent once.
The emails contain a list with every assigned topic to the information that no application was assigned.

### Change active Term

Allows you to change the active term.
You can choose a term on the right and confirm your choice with the button on the left.
The active term influences:
- The courses and topics displayed to the student
- The assignments displayed to the staff member
- The assignments that are exported and imported
- the applications and assignments that are effect by the actions on this page
The active term should always be equal to the term that is currently being worked on (courses being created, applications being created, assignments being done, emails being sent).
A new term can be created via the Django Admin Interface.

### Remove all applications from all slots with errors

Removes all assigned applications from slots that are displayed as a slot with Errors on the home page.

## Teachers Page

Teacher accounts needs to be created from an administrator. (See "Roles -> Teacher")

If you are logged in as a teacher you will get redirected on login, or can access the teachers page by clicking on the "Teachers Page" button in the navigation bar at the top while on the home page.
The page can also be reached at `.../teachers/`.

### Your Courses / Topics

On the left you can see all courses and topics that you have created.
By pressing on the plus button at the bottom of the list you can create a new course or a new topic.
After entering all necessary information you can save the new course or topic by pressing the "Create" button.
By clicking on the edit on the right of a course or topic you can edit it.

### Details

By clicking on a topic you can view information about the topic.
At the bottom all students that have applied for the topic are listed.
On the left are the slots students were assigned and on the right are students that have applied to the topic but have not been yet been assigned to a slot. Note that you cannot make any assignments on this page.

## Roles

### Student

After creating a default account at the login users can create a student account at `.../profile/`.
With a student account you can apply for topics and view your applications.

### Staff Member

Staff members can access and use the home and assignment page.
you can make an existing account a staff account via the Django Admin Interface by selecting the user in the user section and setting the staff-status checkmark.

### Teacher

Teachers can create courses and topics.
They can also view the applications and assignments of their topics.
You can make an existing account a teacher account via the Django Admin Interface by selecting the user in the user section and adding the teacher group to its selected group.

### Administrator

Administrators can access and use all pages.
An admin account can be created in the command via `python manage.py createsuperuser`.
Alternatively you can make an existing account an admin account via the Django Admin Interface by selecting the user in the user section and setting the administrator-status checkmark.