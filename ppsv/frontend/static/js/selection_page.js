var checkedCheckboxes = [];

// checkbox checked -> welche zeile ? -> welche id ? ->

function sendCourseInfos(checkbox) {

   var table = document.getElementById("course_table")

   var rows = table.rows;

   for (i = 1; i < rows.length; i++) {

   var row = rows.item(i).cells;

   if (row.item(0).innerText == checkbox.getAttribute('id') && checkbox.checked) {
        checkedCheckboxes.push(row.item(0).innerText);
   } else if (!checkbox.checked) {
        checkedCheckboxes.splice(checkedCheckboxes.indexOf(checkbox.getAttribute('id')),1);
   }

   }

   console.log(checkedCheckboxes)

}

function getCheckedBoxes(){
    return checkedCheckboxes;
}